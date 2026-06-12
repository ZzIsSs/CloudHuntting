# src/s2_booking/cloud_spots.py


from dataclasses import dataclass


@dataclass(frozen=True)
class CloudSpot:
    name: str          
    lat:  float
    lon:  float
   

# Danh sách các điểm săn mây cố định ở Đà Lạt 
CLOUD_SPOTS: list[CloudSpot] = [
    CloudSpot(
        name        = "Đồi chè Cầu Đất",
        lat         = 11.896,
        lon         = 108.536,
    ),
    CloudSpot(
        name        = "Đồi Đa Phú",
        lat         = 11.979,
        lon         = 108.431,
    ),
    CloudSpot(
        name        = "Đồi Du Sinh",
        lat         = 11.936,
        lon         = 108.411,
    ),
    CloudSpot(
        name        = "Đồi Thiên Phúc Đức",
        lat         = 11.972,
        lon         = 108.448,
    ),
    CloudSpot(
        name        = "Trại Mát",
        lat         = 11.938,
        lon         = 108.494,
    ),
    CloudSpot(
        name        = "Đỉnh Hòn Bồ",
        lat         = 11.977,
        lon         = 1108.487,
    ),
    CloudSpot(
        name        = "Đỉnh Pinhatt",
        lat         = 11.884,
        lon         = 108.423,
    ),
    CloudSpot(
        name        = "Đỉnh Langbiang",
        lat         = 12.046,
        lon         = 108.431,
    ),
    CloudSpot(
        name        = "Đồi Robin",
        lat         = 11.928,
        lon         = 108.437,
    ),
    CloudSpot(
        name        = "Đỉnh Rada",
        lat         = 12.044,
        lon         = 108.440,
    ),
]


_SPOT_INDEX: dict[str, CloudSpot] = {s.name: s for s in CLOUD_SPOTS}


def get_spot(name: str) -> CloudSpot | None:
    """Tìm điểm săn mây theo tên tiếng Việt ."""
    
    if name in _SPOT_INDEX:
        return _SPOT_INDEX[name]
    
    name_lower = name.strip().lower()
    for spot in CLOUD_SPOTS:
        if spot.name.lower() == name_lower:
            return spot
    return None


def list_spots() -> list[dict]:
    """Trả về danh sách tất cả điểm săn mây dạng dict."""
    return [
        {
            "name":        s.name,
            "lat":         s.lat,
            "lon":         s.lon,
        }
        for s in CLOUD_SPOTS
    ]