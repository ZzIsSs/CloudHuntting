import requests
from cachetools import TTLCache, cached
from typing import Dict, Any

# Tạo In-memory Cache, lưu tối đa 100 tọa độ trong thời gian 3600 giây (60 phút)
# Điều này thỏa mãn yêu cầu tối ưu chi phí API ở Module 2
weather_cache = TTLCache(maxsize=100, ttl=3600)

class WeatherService:
    @staticmethod
    @cached(cache=weather_cache)
    def fetch_weather_data(lat: float, lon: float) -> Dict[str, Any]:
        """
        Module 2: Lấy dữ liệu thời tiết thực tế từ Open-Meteo.
        Hàm này đã được bọc bởi decorator @cached. Nếu (lat, lon) đã được gọi
        trong vòng 60 phút qua, nó sẽ trả về kết quả từ Cache mà không gọi API lại.
        """
        # Đây là API dự báo (forecast) hoặc thời tiết hiện tại của Open-Meteo
        # Chúng ta lấy thông số hiện tại (current) tương tự với các feature huấn luyện AI
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover_low,cloud_cover_high,dew_point_2m"
            f"&timezone=Asia%2FHo_Chi_Minh"
        )
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current_data = data.get("current", {})
            if not current_data:
                raise ValueError("Không lấy được dữ liệu current weather từ API")
            
            # Gắn nhãn để biết dữ liệu lấy mới (nếu lấy từ cache thì decorator sẽ trả về thẳng object này)
            return {
                "source": "New API Request",
                "temperature_2m": current_data.get("temperature_2m"),
                "relative_humidity_2m": current_data.get("relative_humidity_2m"),
                "wind_speed_10m": current_data.get("wind_speed_10m"),
                "pressure_msl": current_data.get("pressure_msl"),
                "cloud_cover_low": current_data.get("cloud_cover_low"),
                "cloud_cover_high": current_data.get("cloud_cover_high"),
                "dew_point_2m": current_data.get("dew_point_2m"),
                "time": current_data.get("time")
            }
        except requests.exceptions.RequestException as e:
            # Fallback (sẽ xử lý logic fallback chi tiết hơn nếu cần, ở đây trả lỗi trước)
            raise RuntimeError(f"Lỗi khi gọi Open-Meteo API: {str(e)}")

    @staticmethod
    def get_weather(lat: float, lon: float) -> Dict[str, Any]:
        """
        Hàm bao bọc để xử lý nhãn Cache hay New API.
        Do thư viện cachetools tự động trả về giá trị y hệt ban đầu nên ta
        phải check xem nó là cache hay không một cách thủ công qua keys.
        """
        # Tạo tuple key mặc định của cachetools để kiểm tra
        key = (lat, lon)
        is_cached = key in weather_cache
        
        try:
            # Gọi hàm đã có @cached
            data = WeatherService.fetch_weather_data(lat, lon)
            
            # Nếu is_cached là True từ trước khi gọi hàm, tức là dữ liệu lấy từ Cache
            result = dict(data) # Clone dict để không modify cache gốc
            result["source"] = "Cache" if is_cached else "New API Request"
            return result
        except Exception as e:
            # Module 2 Fallback: nếu lỗi, trả về nhãn Fallback (giả lập)
            return {
                "source": "Fallback",
                "error": str(e),
                "temperature_2m": 15.0, # Giá trị giả lập
                "relative_humidity_2m": 90,
                "wind_speed_10m": 2.5,
                "pressure_msl": 1012,
                "cloud_cover_low": 80,
                "cloud_cover_high": 10,
                "dew_point_2m": 14.0
            }
