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
    {"name": "Đỉnh Rada",          "lat": 12.046, "lon": 108.431},
]

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách đường chim bay (km) giữa 2 tọa độ GPS
    theo công thức Haversine.
    """
    R = 6371.0  # Bán kính Trái Đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def scan_nearby_spots(location_name: str, radius_km: float) -> dict:
    """
    Quét toàn bộ HOTSPOTS nằm trong bán kính từ điểm trung tâm.
    Với mỗi điểm tìm được, gọi WeatherService + AI để tính xác suất mây.
    Trả về top 5 địa điểm xếp theo xác suất từ cao xuống thấp.
    """
    # Bước 1: Dịch tên địa điểm trung tâm thành tọa độ GPS
    center_lat, center_lon = get_coordinates(location_name)
    print(f"\n🔎 [Nearby Scan] Trung tâm: {location_name} ({center_lat}, {center_lon}) | Bán kính: {radius_km}km")

    # Bước 2: Lọc các HOTSPOTS nằm trong bán kính
    candidates = []
    for spot in HOTSPOTS:
        dist = haversine_distance(center_lat, center_lon, spot["lat"], spot["lon"])
        if dist <= radius_km:
            candidates.append({
                "name": spot["name"],
                "lat": spot["lat"],
                "lon": spot["lon"],
                "distance_km": dist
            })
    
    print(f"📍 [Nearby Scan] Tìm thấy {len(candidates)} địa điểm trong bán kính {radius_km}km")

    # Bước 3: Với từng điểm, gọi thời tiết + AI dự báo xác suất mây
    results = []
    for spot in candidates:
        try:
            weather_data = WeatherService.get_weather(spot["lat"], spot["lon"])
            probability, suggestion = predict_cloud_probability(weather_data)
            results.append({
                "location_name": spot["name"],
                "lat": spot["lat"],
                "lon": spot["lon"],
                "distance_km": spot["distance_km"],
                "probability": probability,
                "suggestion": suggestion
            })
            print(f"   ✅ {spot['name']}: {probability}% (cách {spot['distance_km']}km)")
        except Exception as e:
            print(f"   ❌ {spot['name']}: Lỗi - {e}")

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
