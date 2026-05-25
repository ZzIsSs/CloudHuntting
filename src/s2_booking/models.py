# src/s2_booking/models.py
"Định nghĩa các model SQLAlchemy cho S2: Place và Booking."

from sqlalchemy import (
    Column, String, Float, Integer,
    Boolean, Text, Enum as SAEnum,
    DateTime, ForeignKey
)
from sqlalchemy.sql import func
import enum
from .database import Base


class BookingStatus(str, enum.Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED    = "failed"


class PlaceCategory(str, enum.Enum):
    CAFE       = "cafe"
    RESTAURANT = "restaurant"
    HOMESTAY   = "homestay"
    HOTEL      = "hotel"
    CAMPING    = "camping"


class Place(Base):
    """
    Địa điểm gần điểm săn mây: quán cà phê, homestay, nhà hàng...
    Dữ liệu lấy từ OpenStreetMap qua fetch_places.py.
    """
    __tablename__ = "places"

    id           = Column(String(20),  primary_key=True)
    name         = Column(String(255), nullable=False)
    category     = Column(SAEnum(PlaceCategory), nullable=False)
    lat          = Column(Float,   nullable=False)
    lon          = Column(Float,   nullable=False)
    address      = Column(Text,    default="")
    province     = Column(String(100), default="Lâm Đồng")
    phone        = Column(String(30),  nullable=True)
    avg_rating   = Column(Float,   default=4.0)
    review_count = Column(Integer, default=0)
    price_level  = Column(Integer, default=2)   # 1=rẻ → 4=đắt
    is_active    = Column(Boolean, default=True)
    is_bookable  = Column(Boolean, default=True)

    # SQLite không có JSON column → lưu dưới dạng Text (JSON string)
    # Khi đọc ra sẽ json.loads(), khi ghi vào sẽ json.dumps()
    amenities_json     = Column(Text, default="[]")
    opening_hours_json = Column(Text, default="{}")
    photos_json        = Column(Text, default="[]")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    """
    Lịch đặt chỗ của user tại một địa điểm.

    Lưu ý: user_id là Integer khớp với User.id bên S3.
    KHÔNG dùng ForeignKey sang bảng users vì S2 không có bảng đó
    (microservice độc lập — loose coupling).
    """
    __tablename__ = "bookings"

    id              = Column(String(20), primary_key=True)
    idempotency_key = Column(String(64), unique=True, nullable=False, index=True)
    user_id         = Column(Integer, nullable=False, index=True)
    place_id        = Column(String(20), ForeignKey("places.id"), nullable=False)
    booking_date    = Column(String(10), nullable=False)  # "YYYY-MM-DD"
    start_time      = Column(String(5),  nullable=False)  # "HH:MM"
    end_time        = Column(String(5),  nullable=False)  # "HH:MM"
    party_size      = Column(Integer, nullable=False)
    status          = Column(
        SAEnum(BookingStatus),
        default=BookingStatus.PENDING,
        nullable=False
    )
    total_price   = Column(Float,   nullable=True)
    notes         = Column(Text,    nullable=True)
    partner_ref   = Column(String(100), nullable=True)
    cancel_reason = Column(Text,    nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())