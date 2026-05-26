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
from src.shared.database import create_tables, SessionLocal
from .routes import router
from src.s3_auth import models, auth

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

def seed_users():
    db = SessionLocal()
    try:
        users_to_seed = [
            {
                "username": "admin",
                "email": "admin@cloudhunting.com",
                "password": "admin123",
                "role": models.RoleEnum.admin
            },
            {
                "username": "moderator",
                "email": "moderator@cloudhunting.com",
                "password": "moderator123",
                "role": models.RoleEnum.moderator
            },
            {
                "username": "user",
                "email": "user@cloudhunting.com",
                "password": "user123",
                "role": models.RoleEnum.user
            }
        ]
        
        for user_data in users_to_seed:
            existing_user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
            if not existing_user:
                hashed = auth.hash_password(user_data["password"])
                new_user = models.User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed,
                    role=user_data["role"]
                )
                db.add(new_user)
                db.commit()
                print(f"[Seeder] Da nap tai khoan: {user_data['username']}")
    except Exception as e:
        print(f"[Seeder] Loi khi nap du lieu: {e}")
        db.rollback()
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    create_tables()
    seed_users()

app.include_router(router)

@app.get("/health", tags=["Health"])
def health():
    return {"service": "s3_auth", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Khởi chạy Service 3 trên cổng 8003
    uvicorn.run("s3_auth.main:app", host="127.0.0.1", port=8003, reload=True)
