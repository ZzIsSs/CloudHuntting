# src/s2_booking/routes.py
"""
Router chỉ nhận request → gọi service → trả response.
Không chứa logic tính toán.
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse

from . import services
from .schemas import (
    PlaceOut, NearbyResponse, AvailabilityResponse,
    BookingCreate, BookingCancel, BookingOut,
)
from .dependencies import get_current_user, CurrentUser
from .middleware import user_required, admin_required

router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# PLACE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/places/nearby", response_model=NearbyResponse, tags=["Places"])
def get_nearby_places(
    lat:         float           = Query(..., description="Vĩ độ"),
    lon:         float           = Query(..., description="Kinh độ"),
    radius_km:   float           = Query(5.0, ge=0.1, le=50),
    category:    str | None      = Query(None),
    price_level: int | None      = Query(None, ge=1, le=4),
    amenities:   list[str] | None = Query(None),
    page:        int             = Query(1, ge=1),
    per_page:    int             = Query(20, ge=1, le=50),
    current_user: CurrentUser    = Depends(get_current_user),
):
    result = services.get_nearby_places(
        lat, lon, radius_km, category, price_level, amenities, page, per_page
    )
    places_out = [PlaceOut(**p.__dict__) for p in result["places"]]
    return NearbyResponse(places=places_out, **{k: result[k] for k in ["page","per_page","total","has_next"]})


@router.get("/places/{place_id}", tags=["Places"])
def get_place(
    place_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    place = services.get_place_by_id(place_id)
    if not place:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy địa điểm id={place_id}")
    return PlaceOut(**place.__dict__)


@router.get("/places/{place_id}/availability", response_model=AvailabilityResponse, tags=["Places"])
def get_availability(
    place_id: str,
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="VD: 2025-12-01"),
    current_user: CurrentUser = Depends(get_current_user),
):
    if not services.get_place_by_id(place_id):
        raise HTTPException(status_code=404, detail=f"Không tìm thấy địa điểm id={place_id}")
    return services.get_place_availability(place_id, date)


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/bookings", status_code=201, tags=["Bookings"])
def create_booking(
    body: BookingCreate,
    # Cho phép user/admin/moderator tạo booking
    current_user: CurrentUser = Depends(user_required),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    """
    Tạo booking mới.
    - 201: booking mới được tạo.
    - 200: idempotency_key đã tồn tại, trả về booking cũ (retry an toàn).
    - 409: khung giờ đã bị đặt.
    Header bắt buộc: Idempotency-Key: <uuid>
    """
    if not idempotency_key:
        raise HTTPException(status_code=422, detail="Header 'Idempotency-Key' là bắt buộc")

    booking, is_new = services.create_booking(
        user_id         = current_user.id,
        data            = body,
        idempotency_key = idempotency_key,
    )
    out = BookingOut(**booking.__dict__)
    return JSONResponse(
        status_code=201 if is_new else 200,
        content=out.model_dump()
    )


@router.get("/bookings", tags=["Bookings"])
def list_bookings(
    status: str | None    = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
):
    """user thấy booking của mình. admin thấy tất cả."""
    bookings = services.list_bookings(
        user_id       = current_user.id,
        role          = current_user.role,
        status_filter = status,
    )
    return [BookingOut(**b.__dict__) for b in bookings]


@router.get("/bookings/{booking_id}", tags=["Bookings"])
def get_booking(
    booking_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    booking = services.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Không tìm thấy booking")
    if current_user.role != "admin" and booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền xem booking này")
    return BookingOut(**booking.__dict__)


@router.patch("/bookings/{booking_id}/cancel", tags=["Bookings"])
def cancel_booking(
    booking_id: str,
    body: BookingCancel,
    current_user: CurrentUser = Depends(get_current_user),
):
    booking = services.cancel_booking(
        booking_id = booking_id,
        user_id    = current_user.id,
        role       = current_user.role,
        data       = body,
    )
    return BookingOut(**booking.__dict__)