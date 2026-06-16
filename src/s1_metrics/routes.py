from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import requests
import os
from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))

from .schemas import CloudHuntingRequest, CloudHuntingResponse, SpotResult, SinglePredictRequest, SinglePredictResponse, ConfidenceInfo
from .nearby_service import HOTSPOTS, get_real_distance, find_nearest_hotspot
from .geocoding_service import get_coordinates
from .weather_service import WeatherService
from .ai_service import predict_cloud_probability

router = APIRouter()

def send_log_to_service_5(data: Dict[str, Any]):
    """Gửi log xuống S5"""
    try:
        requests.post(f"{os.getenv('S5_URL', 'http://127.0.0.1:8005')}/api/s5/log", json=data, timeout=2)
    except Exception as e:
        print(f"Không thể gửi log sang S5: {e}")

def get_extended_forecast_confidence(hours_ahead: int) -> ConfidenceInfo:
    """Đánh giá độ tin cậy dựa trên thời gian dự báo."""
    if hours_ahead <= 24:
        return ConfidenceInfo(level="high", percent=90, label="🟢 Rất tin cậy")
    elif hours_ahead <= 72:
        return ConfidenceInfo(level="medium", percent=70, label="🟡 Tin cậy vừa")
    elif hours_ahead <= 168:
        return ConfidenceInfo(level="low", percent=45, label="🟠 Tham khảo")
    else:
        return ConfidenceInfo(level="very_low", percent=25, label="🔴 Rất không chắc chắn")

@router.post("/predict", response_model=CloudHuntingResponse)
def predict_cloud_metrics(request: CloudHuntingRequest, background_tasks: BackgroundTasks):
    """
    Endpoint chính với Smart Fallback 3 Tầng:
    - Tầng 1: Lấy data từ S5 (nhanh ~0.1s, nếu có)
    - Tầng 2A: Lấy hotspot gần nhất (nếu ngoài vùng)
    - Tầng 2B/3: Fallback real-time (API Open-Meteo)
    """
    try:
        center_lat, center_lon = get_coordinates(request.location_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi tìm tọa độ: {str(e)}")

    candidates = []
    for spot in HOTSPOTS:
        dist = get_real_distance(center_lat, center_lon, spot["lat"], spot["lon"])
        if dist <= request.radius_km:
            candidates.append({"spot": spot, "dist": dist})

    is_estimated = False
    estimated_from = None
    estimated_distance_km = None
    warning = ""

    if not candidates:
        nearest = find_nearest_hotspot(center_lat, center_lon, max_radius_km=15.0)
        if nearest:
            candidates.append({"spot": nearest, "dist": nearest["distance_km"]})
            is_estimated = True
            estimated_from = nearest["name"]
            estimated_distance_km = nearest["distance_km"]
            warning = f"Dữ liệu ước tính từ trạm quan sát gần nhất cách {nearest['distance_km']}km."
        else:
            dummy = {"name": request.location_name, "lat": center_lat, "lon": center_lon}
            candidates.append({"spot": dummy, "dist": 0.0})
            is_estimated = True
            warning = "Dự báo tính toán trực tiếp cho địa điểm mới (chưa có trạm quan sát dài hạn)."

    s5_url = os.getenv('S5_URL', 'http://127.0.0.1:8005')
    now_vn = datetime.now(VN_TZ)
    target_time = now_vn + timedelta(hours=request.forecast_hours)
    
    top_spots = []
    
    for cand in candidates:
        spot = cand["spot"]
        dist = cand["dist"]
        s5_data = None
        
        # Tầng 1: Thử lấy data từ S5 nếu là trạm xịn và < 4 ngày (96h)
        if spot.get("name") in [h["name"] for h in HOTSPOTS] and request.forecast_hours <= 96:
            try:
                resp = requests.get(f"{s5_url}/api/s5/forecast/{spot['name']}", timeout=1.0)
                if resp.status_code == 200:
                    data = resp.json()
                    best_match = None
                    if request.forecast_hours == 0 and data.get("current"):
                        best_match = data["current"]
                    else:
                        for item in data.get("forecast", []):
                            item_time = datetime.fromisoformat(item["forecast_for"].replace('Z', ''))
                            if abs((item_time - target_time).total_seconds()) <= 3600:
                                best_match = item
                                break
                    if best_match:
                        s5_data = best_match
            except Exception as e:
                warning += f"S5 Exc {spot['name']}: {str(e)}. "
                pass # Bỏ qua lỗi S5, fallback sang real-time
            
            if not s5_data and spot.get("name") in [h["name"] for h in HOTSPOTS] and request.forecast_hours <= 96:
                warning += f"S5 NoMatch {spot['name']}. "
                
        if s5_data:
            # Đã có data từ S5
            conf = ConfidenceInfo(
                level=s5_data["confidence"]["level"],
                percent=s5_data["confidence"]["percent"],
                label=s5_data["confidence"]["label"]
            )
            top_spots.append(SpotResult(
                rank=0,
                location_name=spot["name"],
                lat=spot["lat"],
                lon=spot["lon"],
                distance_km=dist,
                probability=s5_data["probability"],
                best_time=s5_data["forecast_for"],
                suggestion="Dữ liệu siêu tốc từ hệ thống CloudHunting.",
                timeline=[], # Có thể fetch timeline nếu cần
                confidence=conf
            ))
        else:
            # Tầng 2B/3: Real-time API
            try:
                weather_window = WeatherService.get_weather_window(spot["lat"], spot["lon"], request.forecast_hours)
                probability, best_time, suggestion, timeline = predict_cloud_probability(weather_window)
                conf = get_extended_forecast_confidence(request.forecast_hours)
                
                top_spots.append(SpotResult(
                    rank=0,
                    location_name=spot["name"],
                    lat=spot["lat"],
                    lon=spot["lon"],
                    distance_km=dist,
                    probability=probability,
                    best_time=best_time,
                    suggestion=suggestion,
                    timeline=timeline,
                    confidence=conf
                ))
            except Exception as e:
                print(f"Lỗi Real-time với {spot['name']}: {e}")

    # Sắp xếp và gắn hạng
    top_spots.sort(key=lambda x: (-x.probability, x.distance_km))
    for i, sp in enumerate(top_spots):
        sp.rank = i + 1

    return CloudHuntingResponse(
        center_location=request.location_name,
        center_lat=center_lat,
        center_lon=center_lon,
        radius_km=request.radius_km,
        total_spots_found=len(top_spots),
        top_spots=top_spots[:5],
        is_estimated=is_estimated,
        estimated_from=estimated_from,
        estimated_distance_km=estimated_distance_km,
        warning=warning
    )

@router.post("/predict-single", response_model=SinglePredictResponse)
def predict_single_point(request: SinglePredictRequest, background_tasks: BackgroundTasks):
    """Endpoint nội bộ (S6 -> S1), Đã cập nhật ưu tiên S5"""
    try:
        s5_data = None
        # Ưu tiên S5 nếu điểm nằm trong HOTSPOTS
        if request.location_name in [h["name"] for h in HOTSPOTS]:
            s5_url = os.getenv('S5_URL', 'http://127.0.0.1:8005')
            try:
                resp = requests.get(f"{s5_url}/api/s5/forecast/{request.location_name}", timeout=1.0)
                if resp.status_code == 200:
                    data = resp.json()
                    best_match = None
                    if data.get("current"):
                        best_match = data["current"]
                    else:
                        target_time = datetime.now(VN_TZ)
                        for item in data.get("forecast", []):
                            item_time = datetime.fromisoformat(item["forecast_for"].replace('Z', ''))
                            if abs((item_time - target_time).total_seconds()) <= 3600:
                                best_match = item
                                break
                    if best_match:
                        s5_data = best_match
            except Exception:
                pass
                
        if s5_data:
            return SinglePredictResponse(
                location_name=request.location_name,
                lat=request.lat,
                lon=request.lon,
                probability=s5_data["probability"],
                best_time=s5_data["forecast_for"],
                suggestion="Dữ liệu siêu tốc từ hệ thống CloudHunting."
            )
            
        # Fallback sang Real-time nếu không có S5
        weather_window = WeatherService.get_weather_window(request.lat, request.lon, 0)
        probability, best_time, suggestion, _timeline = predict_cloud_probability(weather_window)
        
        w = weather_window[0] if weather_window else {}
        background_tasks.add_task(send_log_to_service_5, {
            "location_name": request.location_name,
            "lat": request.lat,
            "lon": request.lon,
            "probability": probability,
            "weather_data": {
                "temperature_2m": w.get("temperature_2m", 0),
                "relative_humidity_2m": w.get("relative_humidity_2m", 0),
                "wind_speed_10m": w.get("wind_speed_10m", 0),
                "pressure_msl": w.get("pressure_msl", 0),
                "cloud_cover_low": w.get("cloud_cover_low", 0),
                "cloud_cover_high": w.get("cloud_cover_high", 0),
                "dew_point_2m": w.get("dew_point_2m", 0),
            }
        })
        
        return SinglePredictResponse(
            location_name=request.location_name,
            lat=request.lat,
            lon=request.lon,
            probability=probability,
            best_time=best_time,
            suggestion=suggestion
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dự đoán: {str(e)}")
