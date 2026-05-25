# src/s2_booking/services.py
"""
Toàn bộ logic nghiệp vụ S2.
N.1-N.2: đọc/ghi JSON.
N.3+   : thay _load_places() và _load_bookings() bằng DB query.
         Interface hàm giữ nguyên — routes.py không cần sửa.
"""
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from .models import Place, Booking, BookingStatus
from .schemas import BookingCreate, BookingCancel

DATA_DIR = Path(__file__).parent / "data"


# ── Helpers đọc/ghi JSON (xóa khi có DB) ─────────────────────────────────────

def _load_places() -> list[Place]:
    raw = json.loads((DATA_DIR / "mock_places.json").read_text(encoding="utf-8"))
    return [Place(**p) for p in raw]


def _load_bookings() -> list[Booking]:
    path = DATA_DIR / "mock_bookings.json"
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Booking(**b) for b in raw]


def _save_bookings(bookings: list[Booking]) -> None:
    data = [b.__dict__ for b in bookings]
    (DATA_DIR / "mock_bookings.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# ══════════════════════════════════════════════════════════════════════════════
# PLACE SERVICE
# ══════════════════════════════════════════════════════════════════════════════

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Khoảng cách giữa 2 tọa độ (km). N.3: thay bằng ST_Distance PostGIS."""
    import math
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_nearby_places(
    lat: float,
    lon: float,
    radius_km: float        = 5.0,
    category: str | None    = None,
    price_level: int | None = None,
    amenities: list[str] | None = None,
    page: int               = 1,
    per_page: int           = 20,
) -> dict:
    """
    Tìm địa điểm trong bán kính, sắp xếp theo composite score.
    Score = 60% khoảng cách gần + 40% rating cao.
    """
    results = []
    for p in _load_places():
        if not p.is_active:
            continue
        dist = _haversine_km(lat, lon, p.lat, p.lon)
        if dist > radius_km:
            continue
        if category and p.category != category:
            continue
        if price_level and p.price_level != price_level:
            continue
        if amenities and not all(a in p.amenities for a in amenities):
            continue
        p.distance_km = round(dist, 3)
        results.append(p)

    results.sort(
        key=lambda p: (
            (1.0 - min(p.distance_km / radius_km, 1.0)) * 0.6
            + (p.avg_rating / 5.0) * 0.4
        ),
        reverse=True
    )

    total  = len(results)
    start  = (page - 1) * per_page
    paged  = results[start: start + per_page]

    return {
        "places":   paged,
        "page":     page,
        "per_page": per_page,
        "total":    total,
        "has_next": (start + per_page) < total,
    }


def get_place_by_id(place_id: str) -> Place | None:
    return next((p for p in _load_places() if p.id == place_id), None)


def get_place_availability(place_id: str, date_str: str) -> dict:
    """
    Trả về slot còn trống trong ngày.
    Tất cả slot cố định trừ đi slot có booking active.
    """
    all_slots = [
        "07:00", "08:00", "09:00", "10:00", "11:00",
        "14:00", "15:00", "16:00", "17:00", "19:00", "20:00"
    ]
    booked_starts = {
        b.start_time for b in _load_bookings()
        if b.place_id    == place_id
        and b.booking_date == date_str
        and b.status not in (BookingStatus.CANCELLED, BookingStatus.FAILED)
    }
    return {
        "place_id":        place_id,
        "date":            date_str,
        "available_slots": [s for s in all_slots if s not in booked_starts],
        "booked_slots":    list(booked_starts),
    }


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING SERVICE
# ══════════════════════════════════════════════════════════════════════════════

def create_booking(
    user_id: int,
    data: BookingCreate,
    idempotency_key: str,
) -> tuple[Booking, bool]:
    """
    Tạo booking mới.
    Trả về (booking, is_new).
    is_new=False → idempotent repeat, caller trả HTTP 200.
    is_new=True  → booking mới, caller trả HTTP 201.
    """
    bookings = _load_bookings()

    # ── 1. Idempotency check ──────────────────────────────────────────────────
    existing = next((b for b in bookings if b.idempotency_key == idempotency_key), None)
    if existing:
        return existing, False

    # ── 2. Place tồn tại? ─────────────────────────────────────────────────────
    if not get_place_by_id(data.place_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Không tìm thấy địa điểm id={data.place_id}")

    # ── 3. Conflict: cùng place + ngày + giờ ─────────────────────────────────
    conflict = any(
        b for b in bookings
        if b.place_id     == data.place_id
        and b.booking_date == str(data.booking_date)
        and b.start_time   == data.start_time
        and b.status not in (BookingStatus.CANCELLED, BookingStatus.FAILED)
    )
    if conflict:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Khung giờ này đã được đặt, vui lòng chọn giờ khác")

    # ── 4. Tạo mới ───────────────────────────────────────────────────────────
    new_booking = Booking(
        id               = f"bk-{str(uuid.uuid4())[:8]}",
        idempotency_key  = idempotency_key,
        user_id          = user_id,
        place_id         = data.place_id,
        booking_date     = str(data.booking_date),
        start_time       = data.start_time,
        end_time         = data.end_time,
        party_size       = data.party_size,
        notes            = data.notes,
        status           = BookingStatus.PENDING,
        created_at       = datetime.now(timezone.utc).isoformat(),
    )
    bookings.append(new_booking)
    _save_bookings(bookings)
    return new_booking, True


def list_bookings(
    user_id: int,
    role: str,
    status_filter: str | None = None,
) -> list[Booking]:
    """
    user  → chỉ thấy booking của mình.
    admin → thấy tất cả.
    """
    all_bookings = _load_bookings()
    if role == "admin":
        result = all_bookings
    else:
        result = [b for b in all_bookings if b.user_id == user_id]

    if status_filter:
        result = [b for b in result if b.status == status_filter]
    return result


def get_booking_by_id(booking_id: str) -> Booking | None:
    return next((b for b in _load_bookings() if b.id == booking_id), None)


def cancel_booking(
    booking_id: str,
    user_id: int,
    role: str,
    data: BookingCancel,
) -> Booking:
    """
    Hủy booking.
    admin hủy được mọi booking.
    user chỉ hủy được của mình và khi status còn pending/confirmed.
    """
    from fastapi import HTTPException

    bookings = _load_bookings()
    booking  = next((b for b in bookings if b.id == booking_id), None)

    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy booking")

    if role != "admin" and booking.user_id != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền hủy booking này")

    if booking.status in (BookingStatus.CANCELLED, BookingStatus.FAILED, BookingStatus.COMPLETED):
        raise HTTPException(
            status_code=409,
            detail=f"Không thể hủy booking đang ở trạng thái: {booking.status}"
        )

    booking.status        = BookingStatus.CANCELLED
    booking.cancel_reason = data.reason
    _save_bookings(bookings)
    return booking