from pydantic import BaseModel, Field
from typing import List, Optional

class UserPreferenceRequest(BaseModel):
    user_id: str = Field("guest", description="ID của người dùng (nếu có)")
    start_time: str = Field(..., description="Thời gian xuất phát dự kiến (VD: 04:00)")
    start_location: str = Field("Chợ Đà Lạt", description="Địa chỉ hoặc địa điểm xuất phát")
    max_distance_km: float = Field(30.0, description="Khoảng cách di chuyển tối đa cho phép (km)")
    travel_style: str = Field("Sống ảo nhẹ nhàng", description="Phong cách: 'Sống ảo nhẹ nhàng' hoặc 'Phượt/Trekking'")
    preferred_vibe: str = Field("Thương mại", description="Môi trường: 'Thương mại' hoặc 'Hoang sơ'")
    vehicle_type: str = Field("xe máy", description="Phương tiện: 'xe máy' hoặc 'ô tô'")
    selected_location: Optional[str] = Field(None, description="Tên địa điểm cụ thể muốn xem lịch trình (nếu có)")

class PlanBRequest(UserPreferenceRequest):
    current_target_location: str = Field(..., description="Điểm đến hiện tại đang bị đánh giá là có thời tiết xấu")

class LocationData(BaseModel):
    location_name: str
    lat: float
    lon: float
    probability: float
    best_time: Optional[str] = None
    trend: str = "Đi ngang"
    score: float = 0.0

class ItineraryStep(BaseModel):
    time: str
    action: str
    location: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    note: Optional[str] = None

class ItineraryResponse(BaseModel):
    user_id: str
    recommended_locations: List[LocationData]
    timeline: List[ItineraryStep]
    message: str = "Thành công"

class NotificationResponse(BaseModel):
    id: int
    location_name: str
    message: str
    probability: int
    timestamp: str
