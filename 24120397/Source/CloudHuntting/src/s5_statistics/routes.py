from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import get_db
from . import schemas, services

router = APIRouter()

@router.post("/log", response_model=dict)
def create_log(request: schemas.LogRequest, db: Session = Depends(get_db)):
    """
    Endpoint nội bộ: Service 1 bắn dữ liệu sang để Service 5 lưu trữ.
    (Giữ lại để tương thích ngược hoặc dùng cho fallback)
    """
    try:
        services.save_log(db, request)
        return {"status": "success", "message": "Log saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log-batch", response_model=dict)
def create_log_batch(request: schemas.BatchLogRequest, db: Session = Depends(get_db)):
    """
    Endpoint nội bộ: Nhận batch dữ liệu từ Bot S1. Với mỗi bản ghi, nếu đã tồn tại
    (cùng location + forecast_for), thì cập nhật thay vì tạo mới (UPSERT).
    """
    try:
        services.save_log_batch(db, request.logs)
        return {"status": "success", "count": len(request.logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch log error: {str(e)}")

@router.get("/forecast/{location_name}", response_model=schemas.ForecastResponse)
def get_location_forecast(
    location_name: str,
    db: Session = Depends(get_db)
):
    """
    Trả về dự báo đã được pre-computed cho một địa điểm hotspot,
    bao gồm 30 ngày quá khứ + hiện tại + 4 ngày tương lai.
    Response cực nhanh (~1ms) vì chỉ query SQLite.
    """
    if not location_name or len(location_name) < 3:
        raise HTTPException(status_code=400, detail="Tên địa điểm không hợp lệ.")
        
    data = services.get_location_forecast(db, location_name)
    if not data:
        raise HTTPException(status_code=404, detail="Không có dữ liệu pre-computed cho địa điểm này.")
        
    return data

@router.get("/statistics", response_model=schemas.StatisticsResponse)
def read_statistics(
    location_name: str = Query(..., description="Tên địa điểm cần xem thống kê (VD: Đồi chè Cầu Đất)"),
    days: int = Query(30, ge=1, le=30, description="Khoảng thời gian (tối đa 30 ngày)"),
    db: Session = Depends(get_db)
):
    """
    Module 5: Điểm vào của Luồng truy xuất thống kê từ UI.
    """
    if not location_name or len(location_name) < 3:
        raise HTTPException(status_code=400, detail="Tên địa điểm không hợp lệ.")
        
    data = services.get_statistics(db, location_name, days)
    
    if not data:
        return schemas.StatisticsResponse(
            location_name=location_name,
            days_analyzed=days,
            data=[],
            message="Chưa có dữ liệu cho khoảng thời gian đã chọn."
        )
        
    return schemas.StatisticsResponse(
        location_name=location_name,
        days_analyzed=days,
        data=data,
        message="Thành công"
    )
