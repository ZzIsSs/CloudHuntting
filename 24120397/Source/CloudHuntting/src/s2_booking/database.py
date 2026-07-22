# src/s2_booking/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL


_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
   
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Tạo tất cả bảng nếu chưa tồn tại.
    Gọi một lần khi app khởi động trong main.py.
    """
    from . import models  
    Base.metadata.create_all(bind=engine)
    print(" [S2] Database sẵn sàng.")