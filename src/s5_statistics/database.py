from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Đường dẫn file DB (lưu trong cùng thư mục của S5)
DB_PATH = os.path.join(os.path.dirname(__file__), "cloud_hunting.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Cấu hình connect args cho SQLite (check_same_thread=False để dùng trong web server)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CloudMetricsLog(Base):
    """
    Bảng lưu trữ thông tin lịch sử thời tiết và kết quả dự đoán của Service 1.
    """
    __tablename__ = "cloud_metrics_log"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)  # VD: Cầu Đất, Đồi Đa Phú...
    lat = Column(Float)
    lon = Column(Float)
    probability = Column(Float)                 # Tỷ lệ săn mây thành công
    temperature_2m = Column(Float)
    relative_humidity_2m = Column(Float)
    wind_speed_10m = Column(Float)
    pressure_msl = Column(Float)
    cloud_cover_low = Column(Float)
    cloud_cover_high = Column(Float)
    dew_point_2m = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True) # Thời điểm ghi log

# Hàm khởi tạo database
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency để sử dụng session DB trong FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
