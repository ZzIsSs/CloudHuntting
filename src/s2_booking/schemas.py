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
    id:          str
    name:        str
    category:    str
    lat:         float
    lon:         float
    address:     str
    province:    str
    amenities:   list[str]
    photos:      list[dict]
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

    @computed_field
    @property
    def map_url(self) -> str:
        """
        Link mở Google Maps chỉ đường từ vị trí hiện tại của người dùng tới quán.
        """
        return f"https://www.google.com/maps/dir/?api=1&destination={self.lat},{self.lon}"

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


class CloudSpotItem(BaseModel):
    name: str
    lat:  float
    lon:  float


class NearbySpotResponse(NearbyResponse):
    spot: CloudSpotItem


class NearbyByNameResponse(BaseModel):
    location_name: str
    resolved_lat:  float
    resolved_lon:  float
    places:        list[PlaceOut]
    page:          int
    per_page:      int
    total:         int
    has_next:      bool