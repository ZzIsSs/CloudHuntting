# src/s2_booking/services.py
import json
import math
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from .models import Place, Booking, BookingStatus
from .schemas import BookingCreate, BookingCancel


# ── Geo helper ────────────────────────────────────────────────────────────────

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R    = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dp   = math.radians(lat2 - lat1)
    dl   = math.radians(lon2 - lon1)
    a    = math.sin(dp/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def _to_place_out_data(place: Place, distance_km: float) -> dict:
    """Chuyển ORM Place → dict để tạo PlaceOut schema."""
    return {
        "id":           place.id,
        "name":         place.name,
        "category":     place.category,
        "address":      place.address or "",
        "province":     place.province or "Lâm Đồng",
        "phone":        place.phone,
        "avg_rating":   place.avg_rating,
        "review_count": place.review_count,
        "price_level":  place.price_level,
        "is_bookable":  place.is_bookable,
        "amenities":    json.loads(place.amenities_json  or "[]"),
        "photos":       json.loads(place.photos_json     or "[]"),
        "distance_km":  distance_km,
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
    price_level: int | None       = None,
    amenities:   list[str] | None = None,
    page:        int              = 1,
    per_page:    int              = 20,
) -> dict:
    query = db.query(Place).filter(Place.is_active == True)
    if category:
        query = query.filter(Place.category == category)
    if price_level:
        query = query.filter(Place.price_level == price_level)

    all_places = query.all()

    results = []
    for p in all_places:
        dist = _haversine_km(lat, lon, p.lat, p.lon)
        if dist > radius_km:
            continue
        parsed_amenities = json.loads(p.amenities_json or "[]")
        if amenities and not all(a in parsed_amenities for a in amenities):
            continue
        results.append((p, round(dist, 3)))

    # Composite score: 60% gần + 40% rating cao
    results.sort(
        key=lambda x: (
            (1.0 - min(x[1] / radius_km, 1.0)) * 0.6
            + (x[0].avg_rating / 5.0) * 0.4
        ),
        reverse=True
    )

    total = len(results)
    start = (page - 1) * per_page
    paged = results[start: start + per_page]

    return {
        "places":   [_to_place_out_data(p, d) for p, d in paged],
        "page":     page,
        "per_page": per_page,
        "total":    total,
        "has_next": (start + per_page) < total,
    }


def get_place_by_id(db: Session, place_id: str) -> Place | None:
    return db.query(Place).filter(Place.id == place_id).first()


def get_place_availability(db: Session, place_id: str, date_str: str) -> dict:
    ALL_SLOTS = [
        "07:00","08:00","09:00","10:00","11:00",
        "14:00","15:00","16:00","17:00","19:00","20:00",
    ]
    booked_rows = db.query(Booking.start_time).filter(
        Booking.place_id     == place_id,
        Booking.booking_date == date_str,
        Booking.status.notin_([BookingStatus.CANCELLED, BookingStatus.FAILED])
    ).all()
    booked_starts = {row.start_time for row in booked_rows}
    return {
        "place_id":        place_id,
        "date":            date_str,
        "available_slots": [s for s in ALL_SLOTS if s not in booked_starts],
        "booked_slots":    sorted(booked_starts),
    }


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING SERVICE
# ══════════════════════════════════════════════════════════════════════════════

def create_booking(
    db:              Session,
    user_id:         int,
    data:            BookingCreate,
    idempotency_key: str,
) -> tuple[Booking, bool]:
    # 1. Idempotency — trả về booking cũ nếu key đã tồn tại
    existing = db.query(Booking).filter(
        Booking.idempotency_key == idempotency_key
    ).first()
    if existing:
        return existing, False

    # 2. Place tồn tại?
    place = get_place_by_id(db, data.place_id)
    if not place:
        from fastapi import HTTPException
        raise HTTPException(404, f"Không tìm thấy địa điểm id={data.place_id}")

    # 3. Place có cho đặt không?
    if not place.is_bookable:
        from fastapi import HTTPException
        raise HTTPException(422, f"'{place.name}' không hỗ trợ đặt chỗ trước")

    # 4. Conflict slot
    conflict = db.query(Booking).filter(
        Booking.place_id     == data.place_id,
        Booking.booking_date == str(data.booking_date),
        Booking.start_time   == data.start_time,
        Booking.status.notin_([BookingStatus.CANCELLED, BookingStatus.FAILED])
    ).first()
    if conflict:
        from fastapi import HTTPException
        raise HTTPException(409, "Khung giờ này đã được đặt, vui lòng chọn giờ khác")

    # 5. Tạo booking mới
    new_booking = Booking(
        id              = f"bk-{str(uuid.uuid4())[:8]}",
        idempotency_key = idempotency_key,
        user_id         = user_id,
        place_id        = data.place_id,
        booking_date    = str(data.booking_date),
        start_time      = data.start_time,
        end_time        = data.end_time,
        party_size      = data.party_size,
        notes           = data.notes,
        status          = BookingStatus.PENDING,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking, True


def list_bookings(
    db:            Session,
    user_id:       int,
    role:          str,
    status_filter: str | None = None,
) -> list[Booking]:
    query = db.query(Booking)
    if role != "admin":
        query = query.filter(Booking.user_id == user_id)
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    return query.order_by(Booking.created_at.desc()).all()


def get_booking_by_id(db: Session, booking_id: str) -> Booking | None:
    return db.query(Booking).filter(Booking.id == booking_id).first()


def cancel_booking(
    db:         Session,
    booking_id: str,
    user_id:    int,
    role:       str,
    data:       BookingCancel,
) -> Booking:
    from fastapi import HTTPException
    booking = get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(404, "Không tìm thấy booking")
    if role != "admin" and booking.user_id != user_id:
        raise HTTPException(403, "Không có quyền hủy booking này")
    if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED, BookingStatus.FAILED):
        raise HTTPException(409, f"Không thể hủy booking đang ở trạng thái: {booking.status}")
    booking.status        = BookingStatus.CANCELLED
    booking.cancel_reason = data.reason
    db.commit()
    db.refresh(booking)
    return booking