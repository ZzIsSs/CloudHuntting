from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import contextlib

from .routes import router as s5_router
from .database import init_db, SessionLocal
from .services import cleanup_old_records

# Hàm bọc để apscheduler có thể gọi và tự tạo session
def scheduled_cleanup():
    db = SessionLocal()
    try:
        cleanup_old_records(db)
    finally:
        db.close()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB khi chạy
    init_db()
    
    # Cấu hình Module 4: Tự động chạy ngầm mỗi 24 giờ
    scheduler = BackgroundScheduler()
    # Chạy hàm scheduled_cleanup mỗi ngày 1 lần (interval = 24 hours)
    scheduler.add_job(scheduled_cleanup, 'interval', hours=24)
    scheduler.start()
    print("⏰ [Module 4] Đã khởi động bộ lập lịch dọn dẹp dữ liệu (chạy ngầm mỗi 24h).")
    
    yield # Server chạy ở đây
    
    # Tắt scheduler khi server dừng
    scheduler.shutdown()
    print("🛑 Đã tắt bộ lập lịch.")

app = FastAPI(
    title="Cloud Hunting - Service 5",
    description="Microservice thống kê và dọn dẹp dữ liệu săn mây",
    version="1.0.0",
    lifespan=lifespan
)

# Đăng ký routes
app.include_router(s5_router, prefix="/api/s5", tags=["Statistics"])

if __name__ == "__main__":
    import uvicorn
    # Chạy Service 5 ở port 8005
    uvicorn.run("src.s5_statistics.main:app", host="0.0.0.0", port=8005, reload=True)
