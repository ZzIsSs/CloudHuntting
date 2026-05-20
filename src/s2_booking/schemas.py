# src/s2_booking/schemas.py
from pydantic import BaseModel, computed_field, field_validator, model_validator
from typing import Optional
from datetime import date
import enum


# ── Enums dùng chung trong schema ────────────────────────────────────────────
class PlaceCategoryEnum(str, enum.Enum):
    cafe       = "cafe"
    restaurant = "restaurant"
    homestay   = "homestay"
    hotel      = "hotel"
    camping    = "camping"


# ══════════════════════════════════════════════════════════════════════════════
# PLACE SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class PlaceOut(BaseModel):
    """Dữ liệu địa điểm trả về client."""
    id: str
    name: str
    category: str
    address: str
    avg_rating: float
    review_count: int
    price_level: int
    is_bookable: bool
    amenities: list[str]
    photos: list[dict]
    distance_km: float

    # Tính tự động từ distance_km — không lưu DB
    @computed_field
    @property
    def distance_label(self) -> str:
        if self.distance_km < 1:
            return f"{int(self.distance_km * 1000)}m"
        return f"{self.distance_km:.1f}km"

    # Tự lấy ảnh chính từ mảng photos
    @computed_field
    @property
    def primary_photo_url(self) -> Optional[str]:
        if not self.photos:
            return None
        primary = next((p for p in self.photos if p.get("is_primary")), self.photos[0])
        return primary.get("url")

    model_config = {"from_attributes": True}


class NearbyResponse(BaseModel):
    """Response phân trang cho GET /places/nearby."""
    places: list[PlaceOut]
    page: int
    per_page: int
    total: int
    has_next: bool


class AvailabilityResponse(BaseModel):
    """Slot còn trống / đã bị đặt trong một ngày."""
    place_id: str
    date: str
    available_slots: list[str]
    booked_slots: list[str]


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class BookingCreate(BaseModel):
    """Body request khi tạo booking — POST /bookings."""
    place_id: str
    booking_date: date
    start_time: str   # "HH:MM"
    end_time: str     # "HH:MM"
    party_size: int
    notes: Optional[str] = None

    @field_validator("booking_date")
    @classmethod
    def not_in_past(cls, v):
        if v < date.today():
            raise ValueError("Không thể đặt chỗ cho ngày trong quá khứ")
        return v

    @field_validator("party_size")
    @classmethod
    def valid_party_size(cls, v):
        if not 1 <= v <= 100:
            raise ValueError("Số người phải trong khoảng 1–100")
        return v

    @model_validator(mode="after")
    def end_after_start(self):
        from datetime import datetime
        fmt = "%H:%M"
        try:
            s = datetime.strptime(self.start_time, fmt)
            e = datetime.strptime(self.end_time, fmt)
        except ValueError:
            raise ValueError("Định dạng giờ phải là HH:MM")
        if e <= s:
            raise ValueError("end_time phải sau start_time")
        from datetime import timedelta
        if (e - s) < timedelta(minutes=30):
            raise ValueError("Thời gian đặt tối thiểu 30 phút")
        return self


class BookingCancel(BaseModel):
    """Body request khi hủy booking — PATCH /bookings/{id}/cancel."""
    reason: Optional[str] = None


class BookingOut(BaseModel):
    """Dữ liệu booking trả về client."""
    id: str
    place_id: str
    user_id: int
    status: str
    booking_date: str
    start_time: str
    end_time: str
    party_size: int
    total_price: Optional[float]
    notes: Optional[str]
    partner_ref: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}