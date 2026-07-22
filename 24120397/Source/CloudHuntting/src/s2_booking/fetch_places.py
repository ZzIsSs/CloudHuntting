# src/s2_booking/fetch_places.py

import requests
import json
from pathlib import Path

OUTPUT_FILE = Path(__file__).parent / "data" / "mock_places.json"

# Bounding box Đà Lạt: (lat_min, lon_min, lat_max, lon_max)
DALAT_BBOX = (11.88, 108.38, 12.02, 108.52)

CATEGORY_MAP = {
    "cafe":        "cafe",
    "coffee_shop": "cafe",
    "restaurant":  "restaurant",
    "fast_food":   "restaurant",
    "food_court":  "restaurant",
    "guest_house": "homestay",
    "hostel":      "homestay",
    "hotel":       "hotel",
    "motel":       "hotel",
    "camp_site":   "camping",
}

from .image_urls import get_photo_by_index

# Đếm riêng từng category để gán vòng tròn độc lập khi cào OSM
_category_counters: dict[str, int] = {}


def _next_photo_url(category: str) -> str:
    """Fallback: URL ảnh vòng tròn từ image_urls.py theo category."""
    idx = _category_counters.get(category, 0)
    _category_counters[category] = idx + 1
    return get_photo_by_index(category, idx)


def _extract_osm_image(tags: dict) -> str | None:
    """
    Ưu tiên 1: lấy ảnh thật từ OSM tags nếu có.
    Thứ tự: image → wikimedia_commons → mapillary
    """
    raw = tags.get("image") or tags.get("wikimedia_commons") or tags.get("mapillary")
    if not raw:
        return None
    if raw.startswith("File:"):
        filename = raw.replace("File:", "").replace(" ", "_")
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=800"
    if raw.startswith("http"):
        return raw
    return None


def fetch_from_overpass() -> list[dict]:
    lat_min, lon_min, lat_max, lon_max = DALAT_BBOX
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="cafe"]({lat_min},{lon_min},{lat_max},{lon_max});
      node["amenity"="restaurant"]({lat_min},{lon_min},{lat_max},{lon_max});
      node["amenity"="fast_food"]({lat_min},{lon_min},{lat_max},{lon_max});
      node["tourism"="guest_house"]({lat_min},{lon_min},{lat_max},{lon_max});
      node["tourism"="hostel"]({lat_min},{lon_min},{lat_max},{lon_max});
      node["tourism"="hotel"]({lat_min},{lon_min},{lat_max},{lon_max});
      node["tourism"="camp_site"]({lat_min},{lon_min},{lat_max},{lon_max});
    );
    out body;
    """
    print("🌐 Đang gọi Overpass API...")
    resp = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        timeout=30,
        headers={"User-Agent": "CloudHuntingApp/1.0 (educational project)"},
    )
    resp.raise_for_status()
    data = resp.json()
    print(f"✅ Nhận {len(data['elements'])} node từ OSM")
    return data["elements"]


def _extract_osm_image(tags: dict) -> str | None:
    """Ưu tiên 1: lấy ảnh thật từ OSM tags nếu có."""
    raw = tags.get("image") or tags.get("wikimedia_commons") or tags.get("mapillary")
    if not raw:
        return None
    if raw.startswith("File:"):
        filename = raw.replace("File:", "").replace(" ", "_")
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}?width=800"
    if raw.startswith("http"):
        return raw
    return None


def parse_element(el: dict, index: int) -> dict | None:
    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:vi") or tags.get("name:en")
    if not name:
        return None

    amenity  = tags.get("amenity", "")
    tourism  = tags.get("tourism", "")
    category = CATEGORY_MAP.get(amenity) or CATEGORY_MAP.get(tourism) or "cafe"

    # Amenities
    amenities = ["cloud_view"]
    if tags.get("internet_access") in ("wlan", "yes", "free"):
        amenities.append("wifi")
    if tags.get("outdoor_seating") == "yes":
        amenities.append("outdoor_seating")
    if tags.get("takeaway") == "yes":
        amenities.append("takeaway")
    if category in ("hotel", "homestay") and tags.get("breakfast") == "yes":
        amenities.append("breakfast")

    # Price level
    price_level = 2
    stars = tags.get("stars", "")
    if stars in ("4", "5"):
        price_level = 4
    elif stars == "3":
        price_level = 3
    elif category == "camping":
        price_level = 1

    # Địa chỉ
    parts = [
        tags.get("addr:housenumber", ""),
        tags.get("addr:street", ""),
        tags.get("addr:suburb") or tags.get("addr:ward", ""),
    ]
    address = ", ".join(p for p in parts if p)
    if not address:
        address = "Đà Lạt, Lâm Đồng"
    elif "Đà Lạt" not in address:
        address += ", Đà Lạt"

    # Ưu tiên 1: ảnh thật từ OSM tags (image / wikimedia_commons / mapillary)
    # Ưu tiên 2: ảnh vòng tròn theo category từ image_urls.py
    osm_image = _extract_osm_image(tags)
    photo_url = osm_image if osm_image else _next_photo_url(category)
    photo_source = "osm" if osm_image else "category"

    return {
        "id":           f"pl{index:03d}",
        "name":         name,
        "category":     category,
        "lat":          round(el["lat"], 6),
        "lon":          round(el["lon"], 6),
        "address":      address,
        "province":     "Lâm Đồng",
        "avg_rating":   4.0,
        "review_count": 0,
        "price_level":  price_level,
        "is_active":    True,
        "amenities":    list(set(amenities)),
        "opening_hours": {
            "mon": ["07:00","22:00"], "tue": ["07:00","22:00"],
            "wed": ["07:00","22:00"], "thu": ["07:00","22:00"],
            "fri": ["07:00","23:00"], "sat": ["07:00","23:00"],
            "sun": ["07:00","22:00"],
        },
        "photos": [{
            "url":        photo_url,
            "is_primary": True,
            "caption":    f"{name} - Đà Lạt",
            "source":     photo_source,  # "osm" | "category"
        }],
    }


def main():
    try:
        elements = fetch_from_overpass()
    except Exception as e:
        print(f"❌ Lỗi gọi API: {e}")
        return

    places     = []
    seen_names = set()
    index      = 1
    osm_count  = 0

    for el in elements:
        place = parse_element(el, index)
        if not place:
            continue
        if place["name"] in seen_names:
            continue
        seen_names.add(place["name"])
        if place["photos"][0]["source"] == "osm":
            osm_count += 1
        places.append(place)
        index += 1

    order = {"cafe": 0, "restaurant": 1, "homestay": 2, "hotel": 3, "camping": 4}
    places.sort(key=lambda p: order.get(p["category"], 99))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(places, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    from collections import Counter
    cats = Counter(p["category"] for p in places)
    print("\n📍 Kết quả:")
    for cat, count in sorted(cats.items(), key=lambda x: order.get(x[0], 99)):
        print(f"   {cat:12s}: {count}")
    print(f"   {'TỔNG':12s}: {len(places)}")
    print(f"\n🖼️  Ảnh OSM thật  : {osm_count}/{len(places)}")
    print(f"   Ảnh vòng tròn : {len(places) - osm_count}/{len(places)}")
    print(f"\n✅ Ghi xong → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()