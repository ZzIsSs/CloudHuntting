# src/s2_booking/models.py
"Định nghĩa các model SQLAlchemy cho S2: Place."

from sqlalchemy import (
    Column, String, Float, Integer,
    Boolean, Text, Enum as SAEnum,
    DateTime
)
from sqlalchemy.sql import func
import enum
from .database import Base


class PlaceCategory(str, enum.Enum):
    CAFE       = "cafe"
    RESTAURANT = "restaurant"
    HOMESTAY   = "homestay"
    HOTEL      = "hotel"
    CAMPING    = "camping"


class Place(Base):
    """
    Địa điểm gần điểm săn mây: quán cà phê, homestay, nhà hàng...
    Dữ liệu lấy từ OpenStreetMap.
    """
    __tablename__ = "places"

    id           = Column(String(20),  primary_key=True)
    name         = Column(String(255), nullable=False)
    category     = Column(SAEnum(PlaceCategory), nullable=False)
    lat          = Column(Float,   nullable=False)
    lon          = Column(Float,   nullable=False)
    address      = Column(Text,    default="")
    province     = Column(String(100), default="Lâm Đồng")
    is_active    = Column(Boolean, default=True)

    amenities_json     = Column(Text, default="[]")
    opening_hours_json = Column(Text, default="{}")
    photos_json        = Column(Text, default="[]")

    created_at = Column(DateTime(timezone=True), server_default=func.now())