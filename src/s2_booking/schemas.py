# src/s2_booking/schemas.py
from pydantic import BaseModel
from typing import Optional
import enum


class PlaceCategoryEnum(str, enum.Enum):
    cafe       = "cafe"
    restaurant = "restaurant"
    homestay   = "homestay"
    hotel      = "hotel"
    camping    = "camping"


class PlaceOut(BaseModel):
    id:                str
    name:              str
    category:          str
    lat:               float
    lon:               float
    address:           str
    province:          str
    amenities:         list[str]
    photos:            list[dict]
    distance_km:       float
    distance_label:    str
    primary_photo_url: Optional[str] = None
    map_url:           str

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