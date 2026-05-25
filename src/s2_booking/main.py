# src/s2_booking/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routes import router
from . import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Tạo bảng DB
    from .database import init_db
    init_db()

    # 2. Seed nếu DB trống
    from .database import SessionLocal
    from .models import Place
    from .seeder import seed_places
    db = SessionLocal()
    try:
        if db.query(Place).count() == 0:
            print("📦 DB trống — đang seed dữ liệu từ mock_places.json...")
            seed_places(db)
    finally:
        db.close()

    mode = "MOCK" if config.MOCK_AUTH else "JWT (S3)"
    print(f"🚀 S2 Booking | port 8002 | auth={mode}")
    yield
    print("🛑 S2 Booking đã tắt.")


app = FastAPI(
    title="S2 — Đặt chỗ gần điểm săn mây",
    version="1.0.0",
    description="Tìm và đặt chỗ tại các địa điểm lân cận điểm săn mây tại Đà Lạt.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["System"])
def health():
    return {
        "status":    "ok",
        "service":   "s2-booking",
        "version":   "1.0.0",
        "auth_mode": "mock" if config.MOCK_AUTH else "jwt",
    }