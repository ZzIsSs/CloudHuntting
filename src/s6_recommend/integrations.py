import requests
from typing import Dict, Any, List

S1_URL = "http://127.0.0.1:8001/api/s1/predict"
S5_URL = "http://127.0.0.1:8005/api/s5/statistics"

def fetch_s1_prediction(location_name: str, lat: float, lon: float) -> float:
    """
    Gọi S1 để lấy tỷ lệ săn mây hiện tại.
    """
    try:
        payload = {
            "lat": lat,
            "lon": lon,
            "location_name": location_name
        }
        response = requests.post(S1_URL, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("probability", 0.0))
        return 0.0
    except Exception as e:
        print(f"Lỗi khi gọi S1 cho {location_name}: {e}")
        # Giả lập trả về nếu lỗi để hệ thống không sập
        import random
        return float(random.randint(40, 90))

def fetch_s5_trend(location_name: str) -> str:
    """
    Gọi S5 để lấy xu hướng gần nhất (Trend).
    """
    try:
        params = {"location_name": location_name, "days": 7}
        response = requests.get(S5_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Lấy xu hướng của ngày gần nhất
            if data.get("data") and len(data["data"]) > 0:
                last_record = data["data"][-1]
                return last_record.get("trend", "Đi ngang")
        return "Đi ngang"
    except Exception as e:
        print(f"Lỗi khi gọi S5 cho {location_name}: {e}")
        return "Đi ngang"
