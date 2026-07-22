from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .schemas import UserPreferenceRequest, PlanBRequest, ItineraryResponse, NotificationResponse
from .database import get_db, NotificationLog
from .services import save_user_preference, score_locations, generate_itinerary, switch_to_plan_b

router = APIRouter()

@router.post("/recommend", response_model=ItineraryResponse)
def recommend_itinerary(request: UserPreferenceRequest, db: Session = Depends(get_db)):
    """
    Điểm cuối xử lý lộ trình: M1 -> M2 -> M3 -> M4
    """
    try:
        # 1. Lưu lại sở thích người dùng (M1)
        save_user_preference(db, request)
        
        # 2. Đánh giá và chấm điểm địa điểm (M2)
        # Quá trình này sẽ gọi ngầm S1 và S5 thông qua integrations
        best_locations = score_locations(request)
        
        if not best_locations:
            # 3. Kịch bản an toàn (Fallback) thay vì quăng lỗi 404
            itinerary = generate_itinerary(request, [], is_safe_fallback=True)
            return itinerary
            
        # 3. Lên lịch trình (M3, M4)
        itinerary = generate_itinerary(request, best_locations)
        
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    """
    Trả về danh sách các cảnh báo săn mây gần đây nhất (News Feed).
    Sắp xếp mới nhất lên đầu, lấy tối đa 50 cảnh báo.
    """
    notifications = db.query(NotificationLog).order_by(NotificationLog.id.desc()).limit(50).all()
    return notifications

@router.post("/plan-b", response_model=ItineraryResponse)
def get_plan_b(request: PlanBRequest, db: Session = Depends(get_db)):
    """
    Điểm cuối xử lý bẻ lái (Plan B): Người dùng đang trên đường nhưng thời tiết đổi biến.
    """
    try:
        save_user_preference(db, request)
        itinerary = switch_to_plan_b(request)
        return itinerary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
