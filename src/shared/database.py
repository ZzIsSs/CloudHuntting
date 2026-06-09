from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# SQLite cần connect_args này; PostgreSQL/MySQL không cần
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: cấp DB session cho mỗi request, đảm bảo đóng sau khi xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Tạo tất cả bảng từ metadata (gọi khi startup)."""
    Base.metadata.create_all(bind=engine)
