from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .routes import router as s1_router
from .ai_service import load_model

app = FastAPI(
    title="Cloud Hunting - Service 1",
    description="Microservice dự báo tỷ lệ săn mây dựa trên mô hình AI",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    print("[INFO] Đang khởi động Service 1...")
    # Load model vào RAM ngay khi startup (dùng load_model đã import ở đầu file)
    load_model()
    print("[INFO] Service 1 đã sẵn sàng.")

# Đăng ký routes
app.include_router(s1_router, prefix="/api/s1", tags=["Metrics"])

@app.get("/", include_in_schema=False)
def root():
    """Điều hướng trang chủ mặc định về giao diện Swagger UI"""
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    # Dùng cho việc test chạy trực tiếp file này
    uvicorn.run("src.s1_metrics.main:app", host="0.0.0.0", port=8001, reload=True)
