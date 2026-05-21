# src/s2_booking/models.py

from dataclasses import dataclass, field
from typing import Optional
import enum


class BookingStatus(str, enum.Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED    = "failed"


class PlaceCategory(str, enum.Enum):
    CAFE      = "cafe"
    RESTAURANT = "restaurant"
    HOMESTAY  = "homestay"
    HOTEL     = "hotel"
    CAMPING   = "camping"


@dataclass
class Place:
    """Địa điểm (quán, homestay...) gần điểm săn mây."""
    id: str
    name: str
    category: str            # PlaceCategory
    lat: float
    lon: float
    address: str
    province: str
    avg_rating: float
    review_count: int
    price_level: int         # 1=rẻ → 4=đắt
    is_active: bool
    is_bookable: bool
    amenities: list          # ["wifi", "parking", "mountain_view"]
    opening_hours: dict      # {"mon": ["07:00","22:00"], "sun": null}
    photos: list             # [{"url": "...", "is_primary": true}]
    phone: Optional[str]     = None
    distance_km: float       = 0.0   # tính động, không lưu trong JSON


@dataclass
class Booking:
    """Thông tin một lượt đặt chỗ."""
    id: str
    idempotency_key: str     # client tự sinh UUID, ngăn double-booking khi retry
    user_id: int             # int — khớp với int(sub) từ JWT của S3
    place_id: str
    booking_date: str        # "YYYY-MM-DD"
    start_time: str          # "HH:MM"
    end_time: str            # "HH:MM"
    party_size: int
    status: str              # BookingStatus
    created_at: str
    total_price: Optional[float] = None
    notes: Optional[str]         = None
    partner_ref: Optional[str]   = None
    cancel_reason: Optional[str] = None