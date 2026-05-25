# src/s2_booking/routes.py
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import services
from .database import get_db
from .schemas import (
    PlaceOut, NearbyResponse, AvailabilityResponse,
    BookingCreate, BookingCancel, BookingOut,
)
from .dependencies import get_current_user, CurrentUser
from .middleware import user_required

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# PLACE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/places/nearby", response_model=NearbyResponse, tags=["Places"])
def get_nearby_places(
    lat:         float            = Query(..., description="Vĩ độ"),
    lon:         float            = Query(..., description="Kinh độ"),
    radius_km:   float            = Query(5.0, ge=0.1, le=50),
    category:    str | None       = Query(None),
    price_level: int | None       = Query(None, ge=1, le=4),
    amenities:   list[str] | None = Query(None),
    page:        int              = Query(1, ge=1),
    per_page:    int              = Query(20, ge=1, le=50),
    current_user: CurrentUser     = Depends(get_current_user),
    db: Session                   = Depends(get_db),
):
    result = services.get_nearby_places(
        db, lat, lon, radius_km, category, price_level, amenities, page, per_page
    )
    return NearbyResponse(
        places   = [PlaceOut(**p) for p in result["places"]],
        page     = result["page"],
        per_page = result["per_page"],
        total    = result["total"],
        has_next = result["has_next"],
    )


@router.get("/places/{place_id}", response_model=PlaceOut, tags=["Places"])
def get_place(
    place_id:     str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session               = Depends(get_db),
):
    place = services.get_place_by_id(db, place_id)
    if not place:
        raise HTTPException(404, f"Không tìm thấy địa điểm id={place_id}")
    return PlaceOut(**services._to_place_out_data(place, 0.0))


@router.get("/places/{place_id}/availability",
            response_model=AvailabilityResponse, tags=["Places"])
def get_availability(
    place_id:     str,
    date: str     = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$",
                          description="Ngày cần kiểm tra, VD: 2025-12-25"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session               = Depends(get_db),
):
    if not services.get_place_by_id(db, place_id):
        raise HTTPException(404, f"Không tìm thấy địa điểm id={place_id}")
    return services.get_place_availability(db, place_id, date)


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/bookings", status_code=201, tags=["Bookings"])
def create_booking(
    body:            BookingCreate,
    current_user:    CurrentUser   = Depends(user_required),
    idempotency_key: str | None    = Header(default=None, alias="Idempotency-Key"),
    db: Session                    = Depends(get_db),
):
    if not idempotency_key:
        raise HTTPException(422, "Header 'Idempotency-Key' là bắt buộc")

    booking, is_new = services.create_booking(
        db, current_user.id, body, idempotency_key
    )
    out = BookingOut(
        id            = booking.id,
        place_id      = booking.place_id,
        user_id       = booking.user_id,
        status        = booking.status,
        booking_date  = booking.booking_date,
        start_time    = booking.start_time,
        end_time      = booking.end_time,
        party_size    = booking.party_size,
        total_price   = booking.total_price,
        notes         = booking.notes,
        partner_ref   = booking.partner_ref,
        cancel_reason = booking.cancel_reason,
        created_at    = str(booking.created_at) if booking.created_at else None,
    )
    return JSONResponse(
        status_code=201 if is_new else 200,
        content=out.model_dump()
    )


@router.get("/bookings", tags=["Bookings"])
def list_bookings(
    status:       str | None  = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session               = Depends(get_db),
):
    bookings = services.list_bookings(db, current_user.id, current_user.role, status)
    return [BookingOut(
        id=b.id, place_id=b.place_id, user_id=b.user_id,
        status=b.status, booking_date=b.booking_date,
        start_time=b.start_time, end_time=b.end_time,
        party_size=b.party_size, total_price=b.total_price,
        notes=b.notes, partner_ref=b.partner_ref,
        cancel_reason=b.cancel_reason,
        created_at=str(b.created_at) if b.created_at else None,
    ) for b in bookings]


@router.get("/bookings/{booking_id}", tags=["Bookings"])
def get_booking(
    booking_id:   str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session               = Depends(get_db),
):
    booking = services.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(404, "Không tìm thấy booking")
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(403, "Không có quyền xem booking này")
    return BookingOut(
        id=booking.id, place_id=booking.place_id, user_id=booking.user_id,
        status=booking.status, booking_date=booking.booking_date,
        start_time=booking.start_time, end_time=booking.end_time,
        party_size=booking.party_size, total_price=booking.total_price,
        notes=booking.notes, partner_ref=booking.partner_ref,
        cancel_reason=booking.cancel_reason,
        created_at=str(booking.created_at) if booking.created_at else None,
    )


@router.patch("/bookings/{booking_id}/cancel", tags=["Bookings"])
def cancel_booking(
    booking_id:   str,
    body:         BookingCancel,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session               = Depends(get_db),
):
    booking = services.cancel_booking(
        db, booking_id, current_user.id, current_user.role, body
    )
    return BookingOut(
        id=booking.id, place_id=booking.place_id, user_id=booking.user_id,
        status=booking.status, booking_date=booking.booking_date,
        start_time=booking.start_time, end_time=booking.end_time,
        party_size=booking.party_size, total_price=booking.total_price,
        notes=booking.notes, partner_ref=booking.partner_ref,
        cancel_reason=booking.cancel_reason,
        created_at=str(booking.created_at) if booking.created_at else None,
    )