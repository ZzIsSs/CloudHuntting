# src/s2_booking/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routes import router
from . import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .database import init_db, SessionLocal
    from .models import Place
    from .seeder import seed_places

    init_db()

    db = SessionLocal()
    try:
        if db.query(Place).count() == 0:
            print("📦 DB trống — đang seed dữ liệu...")
            seed_places(db)
        else:
            count = db.query(Place).count()
            print(f"📍 DB sẵn sàng — {count} địa điểm.")
    finally:
        db.close()

    mode = "MOCK" if config.MOCK_AUTH else "JWT từ S3"
    print(f"🚀 S2 Places | port 8002 | auth={mode}")
    yield
    print("🛑 S2 Places đã tắt.")


app = FastAPI(
    title="S2 — Gợi ý địa điểm gần điểm săn mây",
    version="1.0.0",
    description="""
## Giới thiệu

Service gợi ý địa điểm ăn uống, nghỉ ngơi gần các điểm săn mây tại **Đà Lạt**.
Dữ liệu lấy từ OpenStreetMap — thật, cập nhật.

## Cách dùng

1. Bấm **Authorize** → nhập token
2. Gọi `/places/nearby` với tọa độ điểm săn mây
3. Filter theo `category`, `price_level`, `amenities`
4. Sort theo `distance`, `rating`, hoặc `score`

## Mock tokens (khi MOCK_AUTH=true)
- `dev-token-user` — user thường
- `dev-token-admin` — admin
    """,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["System"])
def health():
    return {
        "status":    "ok",
        "service":   "s2-places",
        "version":   "1.0.0",
        "auth_mode": "mock" if config.MOCK_AUTH else "jwt",
    }