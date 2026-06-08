# src/s2_booking/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import services
from .database import get_db
from .schemas import PlaceOut, NearbyResponse, CategoryItem
from .dependencies import get_current_user, CurrentUser


router = APIRouter()


# ══════════════════════════════════════════════════════════════════════════════
# PLACE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get(
    "/places/nearby",
    response_model=NearbyResponse,
    tags=["Places"],
    summary="Tìm địa điểm gần điểm săn mây",
)
def get_nearby_places(
    lat:         float            = Query(..., description="Vĩ độ, VD: 11.94"),
    lon:         float            = Query(..., description="Kinh độ, VD: 108.44"),
    radius_km:   float            = Query(5.0,  ge=0.1, le=50),
    category:    str | None       = Query(None, description="cafe|restaurant|homestay|hotel|camping"),
    price_level: int | None       = Query(None, ge=1, le=4, description="1=rẻ → 4=đắt"),
    amenities:   list[str] | None = Query(None, description="wifi, parking, cloud_view..."),
    sort_by:     str              = Query("score", description="score | distance | rating"),
    page:        int              = Query(1,  ge=1),
    per_page:    int              = Query(20, ge=1, le=50),
    current_user: CurrentUser     = Depends(get_current_user),
    db: Session                   = Depends(get_db),
):
    """
    Tìm địa điểm ăn uống, nghỉ ngơi gần điểm săn mây tại Đà Lạt.

    - **sort_by=score**: cân bằng khoảng cách và rating (mặc định)
    - **sort_by=distance**: gần nhất trước
    - **sort_by=rating**: đánh giá cao nhất trước
    """
    result = services.get_nearby_places(
        db, lat, lon, radius_km,
        category, price_level, amenities,
        sort_by, page, per_page
    )
    return NearbyResponse(
        places   = [PlaceOut(**p) for p in result["places"]],
        page     = result["page"],
        per_page = result["per_page"],
        total    = result["total"],
        has_next = result["has_next"],
    )


@router.get(
    "/places/categories",
    response_model=list[CategoryItem],
    tags=["Places"],
    summary="Danh sách loại địa điểm",
)
def get_categories(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session               = Depends(get_db),
):
    """Trả về các category kèm số lượng địa điểm hiện có."""
    return services.get_categories(db)


@router.get(
    "/places/search",
    response_model=list[PlaceOut],
    tags=["Places"],
    summary="Tìm kiếm địa điểm theo tên",
)
def search_places(
    q:            str            = Query(..., min_length=2, description="Từ khóa tìm kiếm"),
    lat:          float | None   = Query(None, description="Vĩ độ để tính khoảng cách"),
    lon:          float | None   = Query(None, description="Kinh độ để tính khoảng cách"),
    current_user: CurrentUser    = Depends(get_current_user),
    db: Session                  = Depends(get_db),
):
    """Tìm địa điểm theo tên. Truyền lat/lon để hiển thị khoảng cách."""
    results = services.search_places(db, q, lat, lon)
    return [PlaceOut(**p) for p in results]