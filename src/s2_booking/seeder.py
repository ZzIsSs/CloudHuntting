# src/s2_booking/seeder.py
"""
Đọc mock_places.json và nhập vào SQLite DB.
Tự động gọi trong main.py khi DB trống.
"""
import json
from pathlib import Path
from sqlalchemy.orm import Session
from .models import Place

DATA_DIR = Path(__file__).parent / "data"


def seed_places(db: Session) -> None:
    path = DATA_DIR / "mock_places.json"
    if not path.exists():
        print("⚠️  mock_places.json chưa có. Chạy: python -m src.s2_booking.fetch_places")
        return

    raw    = json.loads(path.read_text(encoding="utf-8"))
    places = []

    for p in raw:
        # Bỏ qua nếu id đã tồn tại
        if db.query(Place).filter(Place.id == p["id"]).first():
            continue

        place = Place(
            id           = p["id"],
            name         = p["name"],
            category     = p["category"],
            lat          = p["lat"],
            lon          = p["lon"],
            address      = p.get("address", ""),
            province     = p.get("province", "Lâm Đồng"),
            phone        = p.get("phone"),
            avg_rating   = p.get("avg_rating", 4.0),
            review_count = p.get("review_count", 0),
            price_level  = p.get("price_level", 2),
            is_active    = p.get("is_active", True),
            is_bookable  = p.get("is_bookable", True),
            amenities_json     = json.dumps(p.get("amenities", []),     ensure_ascii=False),
            opening_hours_json = json.dumps(p.get("opening_hours", {}), ensure_ascii=False),
            photos_json        = json.dumps(p.get("photos", []),        ensure_ascii=False),
        )
        places.append(place)

    if not places:
        print("ℹ️  Không có địa điểm mới cần seed.")
        return

    db.add_all(places)
    db.commit()
    print(f"✅ Đã seed {len(places)} địa điểm vào DB.")