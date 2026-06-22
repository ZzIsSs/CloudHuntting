# src/s2_booking/services.py
import json
import math

from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Place


# Giúp tính khoảng cách giữa 2 điểm GPS (lat/lon) bằng công thức Haversine.

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R    = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dp   = math.radians(lat2 - lat1)
    dl   = math.radians(lon2 - lon1)
    a    = math.sin(dp/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# Phần hình ảnh cho các địa điểm
from .image_urls import get_photo_by_place_id


def _resolve_photos(photos_json: str, category: str, place_id: str) -> list[dict]:
    """
    Trả về danh sách ảnh hợp lệ.
    - Ảnh source="osm" | "category" → giữ nguyên.
    - Ảnh cũ (không có source) → gán vòng tròn theo place_id.
    """
    photos: list[dict] = json.loads(photos_json or "[]")
    fallback_url = get_photo_by_place_id(category, place_id)

    def _fix(photo: dict) -> dict:
        if photo.get("source") in ("osm", "category"):
            return photo
        return {**photo, "url": fallback_url, "source": "category"}

    fixed = [_fix(p) for p in photos]

    if not fixed:
        fixed = [{
            "url":        fallback_url,
            "is_primary": True,
            "caption":    "",
            "source":     "category",
        }]

    return fixed


def _place_to_dict(place: Place, distance_km: float) -> dict:
    photos = _resolve_photos(
        place.photos_json or "[]",
        place.category or "cafe",
        place.id,
    )
    return {
        "id":            place.id,
        "name":          place.name,
        "category":      place.category,
        "lat":           place.lat,
        "lon":           place.lon,
        "address":       place.address or "",
        "province":      place.province or "Lâm Đồng",
        "amenities":     json.loads(place.amenities_json     or "[]"),
        "opening_hours": json.loads(place.opening_hours_json or "{}"),
        "photos":        photos,
        "distance_km":   distance_km,
    }


# ══════════════════════════════════════════════════════════════════════════════
# PLACE SERVICE
# ══════════════════════════════════════════════════════════════════════════════

def get_nearby_places(
    db:          Session,
    lat:         float,
    lon:         float,
    radius_km:   float            = 5.0,
    category:    str | None       = None,
    amenities:   list[str] | None = None,
    page:        int              = 1,
    per_page:    int              = 20,
) -> dict:

    query = db.query(Place).filter(Place.is_active == True)
    if category:
        query = query.filter(Place.category == category.lower().strip())

    results = []
    for p in query.all():
        dist = _haversine_km(lat, lon, p.lat, p.lon)
        if dist > radius_km:
            continue
        if amenities:
            place_amenities = json.loads(p.amenities_json or "[]")
            if not all(a in place_amenities for a in amenities):
                continue
        results.append((p, round(dist, 3)))

    results.sort(key=lambda x: x[1])

    total = len(results)
    start = (page - 1) * per_page
    paged = results[start: start + per_page]

    return {
        "places":   [_place_to_dict(p, d) for p, d in paged],
        "page":     page,
        "per_page": per_page,
        "total":    total,
        "has_next": (start + per_page) < total,
    }


def get_place_by_id(db: Session, place_id: str) -> Place | None:
    return db.query(Place).filter(Place.id == place_id).first()


def search_places(
    db:      Session,
    keyword: str,
    lat:     float | None = None,
    lon:     float | None = None,
) -> list[dict]:
    query = db.query(Place).filter(
        Place.is_active == True,
        Place.name.ilike(f"%{keyword}%"),
    ).limit(20).all()

    results = []
    for p in query:
        dist = _haversine_km(lat, lon, p.lat, p.lon) if lat and lon else 0.0
        results.append(_place_to_dict(p, round(dist, 3)))

    return results


def get_categories(db: Session) -> list[dict]:
    LABELS = {
        "cafe":       "Cà phê",
        "restaurant": "Nhà hàng",
        "homestay":   "Homestay",
        "hotel":      "Khách sạn",
        "camping":    "Cắm trại",
    }
    rows = (
        db.query(Place.category, func.count(Place.id))
        .filter(Place.is_active == True)
        .group_by(Place.category)
        .all()
    )
    return [
        {
            "category": row[0],
            "label":    LABELS.get(row[0], row[0]),
            "count":    row[1],
        }
        for row in rows
    ]