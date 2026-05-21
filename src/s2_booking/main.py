# src/s2_booking/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="S2 — Đặt chỗ gần điểm săn mây",
    version="1.0.0",
    description="Tìm kiếm và đặt chỗ tại các địa điểm lân cận điểm quan sát mây.",
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
    from . import config
    return {
        "status":    "ok",
        "service":   "s2-booking",
        "version":   "1.0.0",
        "auth_mode": "mock" if config.MOCK_AUTH else "jwt",
    }