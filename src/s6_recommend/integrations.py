import os
import requests
from typing import Dict, Any, List

S1_BASE = os.getenv("S1_URL", "http://127.0.0.1:8001")
S5_BASE = os.getenv("S5_URL", "http://127.0.0.1:8005")
S1_URL = f"{S1_BASE}/api/s1/predict-single"
S5_URL = f"{S5_BASE}/api/s5/statistics"

def fetch_s1_prediction(location_name: str, lat: float, lon: float) -> float:
    """
    Gọi S1 endpoint /predict-single để lấy tỷ lệ săn mây tại tọa độ cụ thể.
    """
    try:
        payload = {
            "lat": lat,
            "lon": lon,
            "location_name": location_name
        }
        response = requests.post(S1_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data.get("probability", 0.0))
        print(f"⚠️ S1 trả về status {response.status_code} cho {location_name}")
        return 0.0
    except Exception as e:
        print(f"❌ Lỗi khi gọi S1 cho {location_name}: {e}")
        return 0.0

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
