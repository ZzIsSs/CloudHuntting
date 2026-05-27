from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import requests

from .schemas import CloudHuntingRequest, CloudHuntingResponse, SpotResult
from .nearby_service import scan_nearby_spots

router = APIRouter()

def send_log_to_service_5(data: Dict[str, Any]):
    """
    Module 4: Tương tác hệ thống (Gửi dữ liệu log về Service 5).
    """
    print(f"🔁 Đang gửi log thống kê về Service 5: {data['location_name']} - Top 1: {data['top1_probability']}%")
    try:
        requests.post("http://127.0.0.1:8005/api/s5/log", json=data, timeout=2)
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
        result = scan_nearby_spots(request.location_name, request.radius_km)
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
    
    # Bước 4: Gửi log sang S5 (ghi nhận top 1)
    if top_spots:
        send_log_to_service_5({
            "location_name": request.location_name,
            "lat": result["center_lat"],
            "lon": result["center_lon"],
            "top1_probability": top_spots[0].probability,
            "top1_location": top_spots[0].location_name,
            "probability": top_spots[0].probability,
            "weather_data": {}
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
