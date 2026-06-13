import requests
import math
from .weather_service import WeatherService
from .ai_service import predict_cloud_probability
from .geocoding_service import get_coordinates

# ─── Danh sách 10 địa điểm săn mây cố định tại Đà Lạt ───────────────────────
HOTSPOTS = [
    {"name": "Đồi chè Cầu Đất",   "lat": 11.896, "lon": 108.536},
    {"name": "Đồi Đa Phú",         "lat": 11.979, "lon": 108.431},
    {"name": "Đồi Du Sinh",        "lat": 11.936, "lon": 108.411},
    {"name": "Đồi Thiên Phúc Đức", "lat": 11.972, "lon": 108.448},
    {"name": "Trại Mát",           "lat": 11.938, "lon": 108.494},
    {"name": "Đỉnh Hòn Bồ",       "lat": 11.977, "lon": 108.487},
    {"name": "Đỉnh Pinhatt",       "lat": 11.884, "lon": 108.423},
    {"name": "Đỉnh Langbiang",     "lat": 12.046, "lon": 108.431},
    {"name": "Đồi Robin",          "lat": 11.928, "lon": 108.437},
    {"name": "Đỉnh Rada",          "lat": 12.044, "lon": 108.440},
]

def get_real_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách đường chim bay (Haversine) để triệt tiêu hoàn toàn độ trễ 8-10s.
    """
    R = 6371.0  # Bán kính Trái Đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def find_nearest_hotspot(lat: float, lon: float, max_radius_km: float = 10.0) -> dict | None:
    """
    Tìm hotspot gần nhất trong bán kính max_radius_km. Dùng khoảng cách đường chim bay cho nhanh.
    Phục vụ cho luồng Smart Fallback.
    """
    min_dist = float('inf')
    nearest = None
    
    for spot in HOTSPOTS:
        # Tạm dùng Haversine để ước lượng nhanh
        R = 6371.0
        dlat = math.radians(spot["lat"] - lat)
        dlon = math.radians(spot["lon"] - lon)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat)) * math.cos(math.radians(spot["lat"])) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist = round(R * c, 2)
        
        if dist < min_dist and dist <= max_radius_km:
            min_dist = dist
            nearest = {"name": spot["name"], "lat": spot["lat"], "lon": spot["lon"], "distance_km": dist}
            
    return nearest

def scan_nearby_spots(location_name: str, radius_km: float, forecast_hours: int = 0) -> dict:
    """
    Quét toàn bộ HOTSPOTS nằm trong bán kính từ điểm trung tâm.
    Với mỗi điểm tìm được, gọi WeatherService + AI để tính xác suất mây.
    Trả về top 5 địa điểm xếp theo xác suất từ cao xuống thấp.
    """
    # Bước 1: Dịch tên địa điểm trung tâm thành tọa độ GPS
    center_lat, center_lon = get_coordinates(location_name)
    print(f"\n🔎 [Nearby Scan] Trung tâm: {location_name} ({center_lat}, {center_lon}) | Bán kính: {radius_km}km | Dự báo: +{forecast_hours}h")

    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Bước 2: Lọc các HOTSPOTS nằm trong bán kính (Chạy đa luồng đồng thời)
    candidates = []
    
    def check_distance(spot):
        dist = get_real_distance(center_lat, center_lon, spot["lat"], spot["lon"])
        if dist <= radius_km:
            return {"name": spot["name"], "lat": spot["lat"], "lon": spot["lon"], "distance_km": dist}
        return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_spot = {executor.submit(check_distance, spot): spot for spot in HOTSPOTS}
        for future in as_completed(future_to_spot):
            res = future.result()
            if res:
                candidates.append(res)
    
    print(f"📍 [Nearby Scan] Tìm thấy {len(candidates)} địa điểm trong bán kính {radius_km}km")

    # Bước 3: Với từng điểm, gọi thời tiết + AI dự báo (Chạy đa luồng đồng thời)
    results = []
    
    def check_weather_and_predict(spot):
        try:
            weather_window = WeatherService.get_weather_window(spot["lat"], spot["lon"], forecast_hours)
            probability, best_time, suggestion, _timeline_short = predict_cloud_probability(weather_window)
            
            # Timeline luon lay 24h de co du data ve bieu do
            timeline_hours = max(forecast_hours, 24)
            weather_window_full = WeatherService.get_weather_window(spot["lat"], spot["lon"], timeline_hours)
            _, _, _, timeline = predict_cloud_probability(weather_window_full)
            
            print(f"   [OK] {spot['name']}: {probability}% lúc {best_time} (cách {spot['distance_km']}km) | timeline: {len(timeline)} points")
            return {
                "location_name": spot["name"],
                "lat": spot["lat"],
                "lon": spot["lon"],
                "distance_km": spot["distance_km"],
                "probability": probability,
                "best_time": best_time,
                "suggestion": suggestion,
                "timeline": timeline
            }
        except Exception as e:
            print(f"   ❌ {spot['name']}: Lỗi - {e}")
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_candidate = {executor.submit(check_weather_and_predict, spot): spot for spot in candidates}
        for future in as_completed(future_to_candidate):
            res = future.result()
            if res:
                results.append(res)

    # Bước 4: Sắp xếp: xác suất mây GIẢM DẦN, nếu bằng nhau thì khoảng cách TĂNG DẦN (gần hơn lên trước)
    results.sort(key=lambda x: (-x["probability"], x["distance_km"]))
    top5 = results[:5]

    # Gắn rank (thứ hạng)
    for i, spot in enumerate(top5):
        spot["rank"] = i + 1

    return {
        "center_location": location_name,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "radius_km": radius_km,
        "total_spots_found": len(results),
        "top_spots": top5
    }
