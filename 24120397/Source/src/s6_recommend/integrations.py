import os
import requests
from typing import Dict, Any, List

S1_BASE = os.getenv("S1_URL", "http://127.0.0.1:8001")
S5_BASE = os.getenv("S5_URL", "http://127.0.0.1:8005")
S1_URL = f"{S1_BASE}/api/s1/predict-single"
S5_URL = f"{S5_BASE}/api/s5/statistics"

def fetch_s1_prediction(location_name: str, lat: float, lon: float) -> dict:
    """
    Gọi S1 endpoint /predict (thay vì /predict-single) để lấy mảng dữ liệu 72h tới.
    Bằng cách set radius_km = 1.0, S1 sẽ chỉ đánh giá chính ngọn đồi này.
    """
    try:
        payload = {
            "location_name": location_name,
            "radius_km": 1.0,
            "forecast_hours": 72
        }
        # Gọi thẳng endpoint chính của S1
        S1_PREDICT_URL = f"{S1_BASE}/api/s1/predict"
        response = requests.post(S1_PREDICT_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("top_spots") and len(data["top_spots"]) > 0:
                spot = data["top_spots"][0]
                return {
                    "probability": float(spot.get("probability", 0.0)),
                    "best_time": spot.get("best_time", None)
                }
        print(f"⚠️ S1 trả về status {response.status_code} cho {location_name}")
        return {"probability": 0.0, "best_time": None}
    except Exception as e:
        print(f"❌ Lỗi khi gọi S1 cho {location_name}: {e}")
        return {"probability": 0.0, "best_time": None}

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
