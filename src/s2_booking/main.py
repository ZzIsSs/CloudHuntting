# src/s2_booking/main.py
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Cấu hình đường dẫn và PYTHONPATH để cả tiến trình cha và tiến trình reload (con) nhận biết được package
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(root_dir, "src")

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Thiết lập biến môi trường PYTHONPATH để uvicorn subprocess kế thừa và load module chính xác
os.environ["PYTHONPATH"] = os.pathsep.join([src_dir, root_dir, os.environ.get("PYTHONPATH", "")])

# Sử dụng absolute imports từ package s2_booking
from s2_booking.routes import router
from s2_booking import config

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
    return {
        "status":    "ok",
        "service":   "s2-booking",
        "version":   "1.0.0",
        "auth_mode": "mock" if config.MOCK_AUTH else "jwt",
    }


if __name__ == "__main__":
    import uvicorn
    # Chạy Service 2 ở port 8002
    uvicorn.run("s2_booking.main:app", host="127.0.0.1", port=8002, reload=True)
