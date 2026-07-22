import sys
import os

# Đảm bảo import được module src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.s1_metrics.nearby_service import HOTSPOTS
from src.s1_metrics.weather_service import WeatherService
from src.s1_metrics.ai_service import predict_cloud_probability

print("Đang quét 10 điểm...")
for spot in HOTSPOTS:
    try:
        weather = WeatherService.get_weather(spot["lat"], spot["lon"])
        prob, sug = predict_cloud_probability(weather)
        print(f"\n--- {spot['name']} ---")
        print(f"Tỷ lệ có mây: {prob}%")
        print(f"Nhiệt độ: {weather.get('temperature_2m')}°C | Điểm sương: {weather.get('dew_point_2m')}°C")
        print(f"Độ ẩm: {weather.get('relative_humidity_2m')}%")
        print(f"Mây tầng thấp: {weather.get('cloud_cover_low')}% | Mây tầng cao: {weather.get('cloud_cover_high')}%")
        print(f"Tốc độ gió: {weather.get('wind_speed_10m')} km/h")
    except Exception as e:
        print(f"Lỗi ở {spot['name']}: {e}")
