# src/s2_booking/schemas.py
from pydantic import BaseModel, computed_field
from typing import Optional
import enum


class PlaceCategoryEnum(str, enum.Enum):
    cafe       = "cafe"
    restaurant = "restaurant"
    homestay   = "homestay"
    hotel      = "hotel"
    camping    = "camping"


class PlaceOut(BaseModel):
    id:           str
    name:         str
    category:     str
    address:      str
    province:     str
    avg_rating:   float
    review_count: int
    price_level:  int
    amenities:    list[str]
    photos:       list[dict]
    distance_km:  float

    @computed_field
    @property
    def distance_label(self) -> str:
        if self.distance_km < 1:
            return f"{int(self.distance_km * 1000)}m"
        return f"{self.distance_km:.1f}km"

    @computed_field
    @property
    def price_label(self) -> str:
        return {1: "Rẻ", 2: "Trung bình", 3: "Khá đắt", 4: "Đắt"}.get(self.price_level, "")

    @computed_field
    @property
    def primary_photo_url(self) -> Optional[str]:
        if not self.photos:
            return None
        primary = next((p for p in self.photos if p.get("is_primary")), self.photos[0])
        return primary.get("url")

    model_config = {"from_attributes": True}


class NearbyResponse(BaseModel):
    places:   list[PlaceOut]
    page:     int
    per_page: int
    total:    int
    has_next: bool


class CategoryItem(BaseModel):
    category: str
    label:    str
    count:    int