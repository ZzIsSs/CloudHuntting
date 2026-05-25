from fastapi import FastAPI
from .routes import router as s1_router
from .ai_service import load_model

app = FastAPI(
    title="Cloud Hunting - Service 1",
    description="Microservice dự báo tỷ lệ săn mây dựa trên mô hình AI",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """
    Load mô hình AI khi khởi động server.
    """
    print("🚀 Đang khởi động Service 1...")
    load_model()

# Đăng ký routes
app.include_router(s1_router, prefix="/api/s1", tags=["Metrics"])

if __name__ == "__main__":
    import uvicorn
    # Dùng cho việc test chạy trực tiếp file này
    uvicorn.run("src.s1_metrics.main:app", host="127.0.0.1", port=8001, reload=True)
