"""
CloudHunting API Gateway

Cong trung tam dieu huong toan bo he thong San May.
Client chi can goi den port 8000, Gateway se tu dong
chuyen tiep request den dung microservice phia sau.

  /app/*      -> Frontend (HTML/CSS/JS)
  /api/s1/*   -> S1 Metrics      (port 8001)
  /api/v1/*   -> S2 Booking      (port 8002)
  /auth/*     -> S3 Auth         (port 8003)
  /content/*  -> S4 Content      (port 8003)
  /api/s5/*   -> S5 Statistics   (port 8005)
  /api/s6/*   -> S6 Recommend    (port 8006)
  /health     -> Dashboard suc khoe he thong
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .routes import router
from .config import GATEWAY_HOST, GATEWAY_PORT, SERVICES

app = FastAPI(
    title="CloudHunting API Gateway",
    description=(
        "Cong trung tam duy nhat cua he thong San May Da Lat.\n\n"
        "Tat ca request tu client deu di qua Gateway (port 8000), "
        "sau do duoc tu dong dieu huong den dung microservice phia sau.\n\n"
        "**Danh sach Services:**\n"
        + "\n".join(f"- **{s['name']}**: `{s['prefix']}/*`" for s in SERVICES.values())
    ),
    version="1.0.0",
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routes (proxy) ---
app.include_router(router)

# --- Static Files: Serve frontend assets & SPA ---
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "cloud-hunting-app", "dist")
frontend_dir = os.path.abspath(frontend_dir)
if os.path.isdir(frontend_dir):
    for subFolder in ["assets", "images", "sound", "pic"]:
        sub_path = os.path.join(frontend_dir, subFolder)
        if os.path.isdir(sub_path):
            app.mount(f"/{subFolder}", StaticFiles(directory=sub_path), name=subFolder)

# --- Static Files: Serve project root pic ---
pic_dir = os.path.join(os.path.dirname(__file__), "..", "..", "pic")
pic_dir = os.path.abspath(pic_dir)
if os.path.isdir(pic_dir):
    app.mount("/project_pic", StaticFiles(directory=pic_dir), name="project_pic")

@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok", "message": "Gateway is running"}

@app.get("/app", include_in_schema=False)
async def serve_frontend_spa_app_root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/app/{path:path}", include_in_schema=False)
async def serve_frontend_spa_app(path: str):
    if not os.path.isdir(frontend_dir):
        return {"error": "Frontend dist directory not found"}
    file_path = os.path.join(frontend_dir, path)
    if path and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/", include_in_schema=False)
async def serve_frontend_root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}

@app.get("/{path:path}", include_in_schema=False)
async def serve_root_catch_all(path: str):
    if not os.path.isdir(frontend_dir):
        return {"error": "Frontend dist directory not found"}
    file_path = os.path.join(frontend_dir, path)
    if path and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found"}
# --- Startup event ---
@app.on_event("startup")
async def startup_event():
    print("=" * 58)
    print("       CloudHunting API Gateway")
    print("=" * 58)
    for key, svc in SERVICES.items():
        print(f"  {svc['prefix']:<14} -> {svc['url']}")
    print("-" * 58)
    print(f"  Frontend: http://{GATEWAY_HOST}:{GATEWAY_PORT}/")
    print(f"  Gateway:  http://{GATEWAY_HOST}:{GATEWAY_PORT}")
    print(f"  Swagger:  http://{GATEWAY_HOST}:{GATEWAY_PORT}/docs")
    print("=" * 58)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.gateway.main:app",
        host=GATEWAY_HOST,
        port=GATEWAY_PORT,
        reload=True
    )
