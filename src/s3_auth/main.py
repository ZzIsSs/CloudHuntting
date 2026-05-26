# src/s3_auth/main.py
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Cấu hình đường dẫn và PYTHONPATH để cả tiến trình cha và tiến trình reload (con) nhận biết được package 'shared'
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(root_dir, "src")

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Thiết lập biến môi trường PYTHONPATH để uvicorn subprocess kế thừa và load module chính xác
os.environ["PYTHONPATH"] = os.pathsep.join([src_dir, root_dir, os.environ.get("PYTHONPATH", "")])

from shared.database import engine, Base
from s3_auth.routes import router as auth_router
from s3_auth import models  # Đảm bảo import để các model được đăng ký vào Base.metadata

# Tạo các bảng database nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="S3 — Dịch vụ Xác thực và Phân quyền",
    version="1.0.0",
    description="Microservice quản lý tài khoản, đăng ký, đăng nhập và phân quyền bằng JWT.",
)

# Cấu hình CORS để cho phép giao tiếp giữa các service và frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router (prefix /auth đã được cấu hình trong routes.py)
app.include_router(auth_router)

@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": "s3-auth",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    # Khởi chạy Service 3 trên cổng 8003
    uvicorn.run("s3_auth.main:app", host="127.0.0.1", port=8003, reload=True)

