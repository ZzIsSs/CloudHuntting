"""
Entry point riêng cho s3_auth service.
Chạy độc lập để dev/test:
    uvicorn src.s3_auth.main:app --reload --port 8003
"""
import sys
from pathlib import Path

# Thêm project root (CloudHuntting/) vào sys.path
# để Python tìm được package `shared`
# s3_auth/main.py → parents[0]=s3_auth, parents[1]=src, parents[2]=CloudHuntting
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.shared.database import create_tables
from .routes import router

app = FastAPI(
    title="Auth Service",
    description="Đăng ký, đăng nhập, phân quyền JWT",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_tables()

app.include_router(router)

@app.get("/health", tags=["Health"])
def health():
    return {"service": "s3_auth", "status": "ok"}