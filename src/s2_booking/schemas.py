# src/s2_booking/schemas.py
from pydantic import BaseModel, computed_field, field_validator, model_validator
from typing import Optional
from datetime import date, datetime
import enum


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
    id: str
    name: str
    category: str
    address: str
    province: str
    phone: Optional[str]
    avg_rating: float
    review_count: int
    price_level: int
    is_bookable: bool
    amenities: list[str]
    photos: list[dict]
    distance_km: float

    @computed_field
    @property
    def distance_label(self) -> str:
        if self.distance_km < 1:
            return f"{int(self.distance_km * 1000)}m"
        return f"{self.distance_km:.1f}km"

    @computed_field
    @property
    def primary_photo_url(self) -> Optional[str]:
        if not self.photos:
            return None
        primary = next((p for p in self.photos if p.get("is_primary")), self.photos[0])
        return primary.get("url")

    model_config = {"from_attributes": True}


class NearbyResponse(BaseModel):
    places: list[PlaceOut]
    page: int
    per_page: int
    total: int
    has_next: bool


class AvailabilityResponse(BaseModel):
    place_id: str
    date: str
    available_slots: list[str]
    booked_slots: list[str]


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class BookingCreate(BaseModel):
    place_id: str
    booking_date: date
    start_time: str
    end_time: str
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

    @field_validator("start_time", "end_time")
    @classmethod
    def valid_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Định dạng giờ phải là HH:MM, ví dụ: 09:00")
        return v

    @model_validator(mode="after")
    def end_after_start(self):
        try:
            s = datetime.strptime(self.start_time, "%H:%M")
            e = datetime.strptime(self.end_time,   "%H:%M")
        except ValueError:
            return self
        if e <= s:
            raise ValueError("end_time phải sau start_time")
        from datetime import timedelta
        if (e - s) < timedelta(minutes=30):
            raise ValueError("Thời gian đặt tối thiểu 30 phút")
        return self


class BookingCancel(BaseModel):
    reason: Optional[str] = None


class BookingOut(BaseModel):
    id: str
    place_id: str
    user_id: int
    status: str
    booking_date: str
    start_time: str
    end_time: str
    party_size: int
    total_price: Optional[float] = None
    notes: Optional[str]        = None
    partner_ref: Optional[str]  = None
    cancel_reason: Optional[str] = None
    created_at: Optional[str]   = None

    model_config = {"from_attributes": True}