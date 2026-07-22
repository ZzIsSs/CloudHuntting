# src/s2_booking/cloud_spot.py

import json
from dataclasses import dataclass
from pathlib import Path


HOTSPOTS_FILE = Path(__file__).parent.parent / "shared" / "hotspots.json"


@dataclass(frozen=True)
class CloudSpot:
    name: str
    lat:  float
    lon:  float


def _load_spots() -> list[CloudSpot]:
    if not HOTSPOTS_FILE.exists():
        print(f" Không tìm thấy {HOTSPOTS_FILE}")
        return []

    raw = json.loads(HOTSPOTS_FILE.read_text(encoding="utf-8"))
    return [
        CloudSpot(name=item["name"], lat=item["lat"], lon=item["lon"])
        for item in raw
    ]


CLOUD_SPOTS: list[CloudSpot] = _load_spots()
_SPOT_INDEX: dict[str, CloudSpot] = {s.name: s for s in CLOUD_SPOTS}


def get_spot(name: str) -> CloudSpot | None:
    """Tìm điểm săn mây theo tên tiếng Việt."""
    if name in _SPOT_INDEX:
        return _SPOT_INDEX[name]

    name_lower = name.strip().lower()
    for spot in CLOUD_SPOTS:
        if spot.name.lower() == name_lower:
            return spot
    return None


def list_spots() -> list[dict]:
    """Trả về danh sách tất cả điểm săn mây."""
    return [{"name": s.name, "lat": s.lat, "lon": s.lon} for s in CLOUD_SPOTS]