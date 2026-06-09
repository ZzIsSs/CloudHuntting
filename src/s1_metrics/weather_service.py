import requests
from cachetools import TTLCache, cached
from typing import Dict, Any

# Tạo In-memory Cache, lưu tối đa 100 tọa độ trong thời gian 3600 giây (60 phút)
weather_cache = TTLCache(maxsize=100, ttl=3600)

from datetime import datetime, timedelta, timezone

class WeatherService:
    @staticmethod
    @cached(cache=weather_cache)
    def fetch_weather_forecast(lat: float, lon: float) -> Dict[str, Any]:
        """
        Lấy dữ liệu thời tiết thực tế từ Open-Meteo (dạng hourly) cho 4 ngày.
        Cache lại theo tọa độ.
        """
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover_low,cloud_cover_high,dew_point_2m"
            f"&timezone=Asia%2FHo_Chi_Minh&forecast_days=4"
        )
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            hourly_data = data.get("hourly", {})
            if not hourly_data or "time" not in hourly_data:
                raise ValueError("Không lấy được dữ liệu hourly weather từ API")
            
            return hourly_data
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Lỗi khi gọi Open-Meteo API: {str(e)}")

    @staticmethod
    def get_weather_window(lat: float, lon: float, forecast_hours: int = 0) -> list:
        """
        Trả về mảng (list) các dữ liệu thời tiết từ 'hiện tại' đến 'hiện tại + forecast_hours'
        """
        try:
            hourly_data = WeatherService.fetch_weather_forecast(lat, lon)
            
            # Lấy giờ hiện tại (timezone VN UTC+7) và làm tròn xuống giờ chẵn
            vn_tz = timezone(timedelta(hours=7))
            now = datetime.now(vn_tz)
            now_str = now.strftime("%Y-%m-%dT%H:00")
            
            # Tìm index của giờ hiện tại
            try:
                start_index = hourly_data["time"].index(now_str)
            except ValueError:
                start_time = datetime.strptime(hourly_data["time"][0], "%Y-%m-%dT%H:%M")
                start_time = start_time.replace(tzinfo=vn_tz)
                diff_hours = int((now - start_time).total_seconds() / 3600)
                start_index = max(0, min(diff_hours, len(hourly_data["time"]) - 1))
                
            end_index = min(start_index + forecast_hours, len(hourly_data["time"]) - 1)
            
            # Trích xuất mảng dữ liệu
            window_data = []
            for i in range(start_index, end_index + 1):
                window_data.append({
                    "temperature_2m": hourly_data["temperature_2m"][i],
                    "relative_humidity_2m": hourly_data["relative_humidity_2m"][i],
                    "wind_speed_10m": hourly_data["wind_speed_10m"][i],
                    "pressure_msl": hourly_data["pressure_msl"][i],
                    "cloud_cover_low": hourly_data["cloud_cover_low"][i],
                    "cloud_cover_high": hourly_data["cloud_cover_high"][i],
                    "dew_point_2m": hourly_data["dew_point_2m"][i],
                    "time": hourly_data["time"][i]
                })
            return window_data
        except Exception as e:
            # Fallback cho 1 điểm duy nhất
            return [{
                "error": str(e),
                "temperature_2m": 15.0,
                "relative_humidity_2m": 90,
                "wind_speed_10m": 2.5,
                "pressure_msl": 1012,
                "cloud_cover_low": 80,
                "cloud_cover_high": 10,
                "dew_point_2m": 14.0,
                "time": datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:00")
            }]
