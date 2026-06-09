from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import requests
import os

from .schemas import CloudHuntingRequest, CloudHuntingResponse, SpotResult, SinglePredictRequest, SinglePredictResponse
from .nearby_service import scan_nearby_spots
from .weather_service import WeatherService
from .ai_service import predict_cloud_probability

router = APIRouter()

def send_log_to_service_5(data: Dict[str, Any]):
    """
    Module 4: Tương tác hệ thống (Gửi dữ liệu log về Service 5).
    """
    print(f"🔁 Đang gửi log thống kê về Service 5: {data['location_name']} - {data['probability']}%")
    try:
        requests.post(f"{os.getenv('S5_URL', 'http://127.0.0.1:8005')}/api/s5/log", json=data, timeout=2)
    except Exception as e:
        print(f"Không thể gửi log sang S5: {e}")

@router.post("/predict", response_model=CloudHuntingResponse)
def predict_cloud_metrics(request: CloudHuntingRequest):
    """
    Endpoint chính của Service 1:
    Nhập tên địa điểm + bán kính → Trả về Top 5 địa điểm săn mây tốt nhất.
    
    Ví dụ input: { "location_name": "Hồ Xuân Hương", "radius_km": 15 }
    """
    # Bước 1: Quét toàn bộ HOTSPOTS trong bán kính
    try:
        result = scan_nearby_spots(request.location_name, request.radius_km, request.forecast_hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
    
    # Bước 2: Kiểm tra có tìm được địa điểm nào không
    if result["total_spots_found"] == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy địa điểm săn mây nào trong bán kính {request.radius_km}km từ '{request.location_name}'. Hãy thử tăng bán kính lên."
        )
    
    # Bước 3: Chuyển đổi kết quả thành Pydantic models
    top_spots = [SpotResult(**spot) for spot in result["top_spots"]]
    
    # Bước 4: Gửi log sang S5 (ghi nhận top 1) với weather_data đầy đủ
    if top_spots:
        top1 = top_spots[0]
        # Lấy weather data thực tế cho top 1 để gửi log
        try:
            weather_window = WeatherService.get_weather_window(top1.lat, top1.lon, 0)
            w = weather_window[0] if weather_window else {}
            weather_payload = {
                "temperature_2m": w.get("temperature_2m", 0),
                "relative_humidity_2m": w.get("relative_humidity_2m", 0),
                "wind_speed_10m": w.get("wind_speed_10m", 0),
                "pressure_msl": w.get("pressure_msl", 0),
                "cloud_cover_low": w.get("cloud_cover_low", 0),
                "cloud_cover_high": w.get("cloud_cover_high", 0),
                "dew_point_2m": w.get("dew_point_2m", 0),
            }
        except Exception:
            weather_payload = {
                "temperature_2m": 0, "relative_humidity_2m": 0, "wind_speed_10m": 0,
                "pressure_msl": 0, "cloud_cover_low": 0, "cloud_cover_high": 0, "dew_point_2m": 0,
            }
        
        send_log_to_service_5({
            "location_name": top1.location_name,
            "lat": top1.lat,
            "lon": top1.lon,
            "probability": top1.probability,
            "weather_data": weather_payload
        })
    
    # Bước 5: Trả về kết quả
    return CloudHuntingResponse(
        center_location=result["center_location"],
        center_lat=result["center_lat"],
        center_lon=result["center_lon"],
        radius_km=result["radius_km"],
        total_spots_found=result["total_spots_found"],
        top_spots=top_spots
    )

@router.post("/predict-single", response_model=SinglePredictResponse)
def predict_single_point(request: SinglePredictRequest):
    """
    Endpoint nội bộ: Nhận tọa độ GPS trực tiếp → Trả về dự báo cho 1 điểm.
    Dùng cho tích hợp S6 → S1 (không cần geocoding, không quét nhiều hotspot).
    
    Ví dụ input: { "lat": 11.979, "lon": 108.431, "location_name": "Đồi Đa Phú" }
    """
    try:
        # Lấy thời tiết hiện tại (forecast_hours=0 → 1 datapoint)
        weather_window = WeatherService.get_weather_window(request.lat, request.lon, 0)
        
        # Chạy AI prediction
        probability, best_time, suggestion, _timeline = predict_cloud_probability(weather_window)
        
        # Gửi log sang S5
        w = weather_window[0] if weather_window else {}
        send_log_to_service_5({
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

