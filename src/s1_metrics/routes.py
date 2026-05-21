from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import requests

from .schemas import CloudHuntingRequest, CloudHuntingResponse
from .weather_service import WeatherService
from .ai_service import predict_cloud_probability

router = APIRouter()

def send_log_to_service_5(data: Dict[str, Any]):
    """
    """
    Module 4: Tương tác hệ thống (Gửi dữ liệu log về Service 5).
    """
    # Gọi thẳng sang Service 5
    print(f"🔁 Đang gửi log thống kê về Service 5: Tọa độ ({data['lat']}, {data['lon']}) - Tỷ lệ: {data['probability']}%")
    try:
        requests.post("http://127.0.0.1:8005/api/s5/log", json=data, timeout=2)
    except Exception as e:
        print(f"Không thể gửi log sang S5: {e}")

@router.post("/predict", response_model=CloudHuntingResponse)
def predict_cloud_metrics(request: CloudHuntingRequest):
    """
    Endpoint chính: Phân tích chỉ số tức thời.
    Nhận tọa độ, lấy thời tiết, chạy AI, và trả kết quả.
    """
    # Bước 1 & 2: Dữ liệu (lat, lon) đã được validate bởi schemas.py
    lat, lon = request.lat, request.lon
    
    # Bước 3: Lấy dữ liệu thời tiết (Module 2)
    weather_data = WeatherService.get_weather(lat, lon)
    
    if weather_data.get("error") and weather_data.get("source") != "Fallback":
        raise HTTPException(status_code=500, detail="Không thể lấy dữ liệu thời tiết.")
        
    # Bước 4: Chạy AI (Module 3)
    try:
        probability, suggestion = predict_cloud_probability(weather_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống AI: {str(e)}")
        
    # Bước 5: Đóng gói kết quả và gửi log S5 (Module 4)
    response_data = CloudHuntingResponse(
        probability=probability,
        suggestion=suggestion,
        weather_data=weather_data,
        data_source=weather_data.get("source", "Unknown")
    )
    
    # Gửi log sang S5
    send_log_to_service_5({
        "location_name": request.location_name,
        "lat": lat,
        "lon": lon,
        "probability": probability,
        "weather_data": weather_data
    })
    
    return response_data
