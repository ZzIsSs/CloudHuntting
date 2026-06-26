# src/s2_booking/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import services
from .geocoding import get_coordinates
from .cloud_spot import get_spot, list_spots
from .database import get_db
from .schemas import PlaceOut, NearbyResponse, CategoryItem, CloudSpotItem, NearbySpotResponse, NearbyByNameResponse
from .dependencies import get_current_user, CurrentUser


router = APIRouter()


# Dùng GPS tìm quán gần đó

@router.get(
    "/places/nearby",
    response_model=NearbyResponse,
    tags=["Places"],
    summary="Gợi ý địa điểm gần (theo GPS người dùng)",
)
def get_nearby_places(
    lat:         float            = Query(..., description="Vĩ độ"),
    lon:         float            = Query(..., description="Kinh độ"),
    radius_km:   float            = Query(5.0,  ge=0.1, le=50),
    category:    str | None       = Query(None, description="Loại quán: cafe | restaurant | homestay | hotel | camping"),
    amenities:   list[str] | None = Query(None, description="Yêu cầu: wifi, parking, cloud_view..."),
    page:        int              = Query(1,  ge=1, description="Trang hiện tại"),
    per_page:    int              = Query(20, ge=1, le=50, description="Số địa điểm mỗi trang"),
    current_user: CurrentUser     = Depends(get_current_user),
    db: Session                   = Depends(get_db),
):
    """
    Tìm địa điểm ăn uống, nghỉ ngơi gần GPS người dùng.
    Sắp xếp theo khoảng cách gần nhất trước.
    """
    result = services.get_nearby_places(
        db, lat, lon, radius_km,
        category.lower().strip() if category else None, amenities,
        page=page, per_page=per_page,
    )
    return NearbyResponse(
        places   = [PlaceOut(**p) for p in result["places"]],
        page     = result["page"],
        per_page = result["per_page"],
        total    = result["total"],
        has_next = result["has_next"],
    )


@router.get(
    "/places/nearby-by-name",
    response_model=NearbyByNameResponse,
    tags=["Places"],
    summary="Gợi ý địa điểm gần (theo tên)",
)
def get_nearby_by_name(
    location_name: str            = Query(..., description="Tên địa điểm"),
    radius_km:     float          = Query(5.0, ge=0.1, le=50),
    category:      str | None     = Query(None),
    page:          int            = Query(1, ge=1),
    per_page:      int            = Query(20, ge=1, le=50),
    current_user:  CurrentUser    = Depends(get_current_user),
    db: Session                   = Depends(get_db),
):
    # Geocoding: tên → tọa độ
    lat, lon = get_coordinates(location_name)

    # Tìm quán gần tọa độ đó
    result = services.get_nearby_places(
        db, lat, lon, radius_km,
        category.lower().strip() if category else None,
        page=page, per_page=per_page,
    )

    return NearbyByNameResponse(
        location_name = location_name,
        resolved_lat  = lat,
        resolved_lon  = lon,
        places        = [PlaceOut(**p) for p in result["places"]],
        page          = result["page"],
        per_page      = result["per_page"],
        total         = result["total"],
        has_next      = result["has_next"],
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
    """Trả về các category kèm số lượng địa điểm hiện có trong database."""
    return services.get_categories(db)


@router.get(
    "/places/search",
    response_model=list[PlaceOut],
    tags=["Places"],
    summary="Tìm kiếm địa điểm quán theo tên",
)
def search_places(
    q:            str            = Query(..., min_length=2, description="Tên địa điểm quán cần tìm kiếm"),
    lat:          float | None   = Query(None, description="Vĩ độ để tính khoảng cách đến địa điểm"),
    lon:          float | None   = Query(None, description="Kinh độ để tính khoảng cách đến địa điểm"),
    current_user: CurrentUser    = Depends(get_current_user),
    db: Session                  = Depends(get_db),
):
    """Truyền lat/lon để hiển thị khoảng cách đến địa điểm đó."""
    results = services.search_places(db, q.strip(), lat, lon)
    return [PlaceOut(**p) for p in results]


# Tiện ích khi người dùng xem điểm săn mây

@router.get(
    "/spots",
    response_model=list[CloudSpotItem],
    tags=["Cloud Spots"],
    summary="Danh sách các địa điểm săn mây cố định tại Đà Lạt",
)
def get_cloud_spots(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Trả về các điểm săn mây cố định tại Đà Lạt, kèm tọa độ."""
    return list_spots()


@router.get(
    "/spots/nearby",
    response_model=NearbySpotResponse,
    tags=["Cloud Spots"],
    summary="Gợi ý địa điểm xung quanh điểm săn mây cố định",
)
def get_places_near_spot(
    spot:         str          = Query(..., description="Tên địa điểm săn mây, VD: Đỉnh Langbiang"),
    radius_km:    float        = Query(5.0, ge=0.1, le=20, description="Mặc định 5km"),
    category:     str | None   = Query(None, description="Loại quán: cafe | restaurant | homestay | hotel | camping"),
    page:         int          = Query(1, ge=1),
    per_page:     int          = Query(20, ge=1, le=50),
    current_user: CurrentUser  = Depends(get_current_user),
    db: Session                = Depends(get_db),
):
    """
    Flow:
    1. S1 hiển thị danh sách cloud_spot trong bán kính quét
    2. Người dùng bấm **Tiện ích** trên một cloud_spot
    3. Frontend gọi endpoint này với `spot=<tên điểm>`
    4. S2 tra tọa độ, trả về địa điểm trong bán kính xung quanh điểm săn mây đó.
    """
    cloud_spot = get_spot(spot)
    if not cloud_spot:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy điểm săn mây '{spot}'. Xem danh sách tại GET /api/v1/spots",
        )

    result = services.get_nearby_places(
        db, cloud_spot.lat, cloud_spot.lon, radius_km,
        category, page=page, per_page=per_page,
        map_origin=(cloud_spot.lat, cloud_spot.lon),
    )

    return NearbySpotResponse(
        spot     = CloudSpotItem(
            name = cloud_spot.name,
            lat  = cloud_spot.lat,
            lon  = cloud_spot.lon,
        ),
        places   = [PlaceOut(**p) for p in result["places"]],
        page     = result["page"],
        per_page = result["per_page"],
        total    = result["total"],
        has_next = result["has_next"],
    )