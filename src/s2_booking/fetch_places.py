# src/s2_booking/fetch_places.py
"""
Lấy địa điểm thật tại Đà Lạt từ OpenStreetMap qua Overpass API.
Miễn phí, không cần API key.

Chạy MỘT LẦN trước khi khởi động app:
    python -m src.s2_booking.fetch_places
"""
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


def parse_element(el: dict, index: int) -> dict | None:
    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:vi") or tags.get("name:en")
    if not name:
        return None

    amenity  = tags.get("amenity", "")
    tourism  = tags.get("tourism", "")
    category = CATEGORY_MAP.get(amenity) or CATEGORY_MAP.get(tourism) or "cafe"

    # Amenities
    amenities = ["cloud_view"]  # tất cả địa điểm ở Đà Lạt đều có view mây
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

    return {
        "id":           f"pl{index:03d}",
        "name":         name,
        "category":     category,
        "lat":          round(el["lat"], 6),
        "lon":          round(el["lon"], 6),
        "address":      address,
        "province":     "Lâm Đồng",
        "phone":        tags.get("phone") or tags.get("contact:phone"),
        "avg_rating":   4.0,
        "review_count": 0,
        "price_level":  price_level,
        "is_active":    True,
        "is_bookable":  category != "camping",
        "amenities":    list(set(amenities)),
        "opening_hours": {
            "mon": ["07:00","22:00"], "tue": ["07:00","22:00"],
            "wed": ["07:00","22:00"], "thu": ["07:00","22:00"],
            "fri": ["07:00","23:00"], "sat": ["07:00","23:00"],
            "sun": ["07:00","22:00"],
        },
        "photos": [{
            "url":        f"https://picsum.photos/seed/{el['id']}/800/600",
            "is_primary": True,
            "caption":    f"{name} - Đà Lạt",
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

    for el in elements:
        place = parse_element(el, index)
        if not place:
            continue
        if place["name"] in seen_names:
            continue
        seen_names.add(place["name"])
        places.append(place)
        index += 1

    # Sắp xếp theo category
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
    print(f"\n✅ Ghi xong → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()