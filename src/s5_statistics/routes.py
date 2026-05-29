from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import get_db
from . import schemas, services

router = APIRouter()

@router.post("/log", response_model=dict)
def create_log(request: schemas.LogRequest, db: Session = Depends(get_db)):
    """
    Endpoint nội bộ: Service 1 bắn dữ liệu sang để Service 5 lưu trữ.
    """
    try:
        services.save_log(db, request)
        return {"status": "success", "message": "Log saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=schemas.StatisticsResponse)
def read_statistics(
    location_name: str = Query(..., description="Tên địa điểm cần xem thống kê (VD: Đồi chè Cầu Đất)"),
    days: int = Query(30, ge=1, le=30, description="Khoảng thời gian (tối đa 30 ngày)"),
    db: Session = Depends(get_db)
):
    """
    Module 5: Điểm vào của Luồng truy xuất thống kê từ UI.
    """
    # Checkpoint 1 (Đã được Pydantic của FastAPI validate tham số 'days')
    # Validate location_name (kiểm tra đơn giản)
    if not location_name or len(location_name) < 3:
        raise HTTPException(status_code=400, detail="Tên địa điểm không hợp lệ.")
        
    data = services.get_statistics(db, location_name, days)
    
    # Checkpoint 2: Nếu không có dữ liệu
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
