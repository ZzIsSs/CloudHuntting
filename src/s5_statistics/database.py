from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint
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
    Bảng lưu trữ thông tin thời tiết và kết quả dự đoán của Service 1.
    Bao gồm cả dữ liệu lịch sử (quá khứ) và dự báo tương lai (forecast).
    """
    __tablename__ = "cloud_metrics_log"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)  # VD: Cầu Đất, Đồi Đa Phú...
    lat = Column(Float)
    lon = Column(Float)
    probability = Column(Float)                 # Tỷ lệ săn mây thành công (%)
    temperature_2m = Column(Float)
    relative_humidity_2m = Column(Float)
    wind_speed_10m = Column(Float)
    pressure_msl = Column(Float)
    cloud_cover_low = Column(Float)
    cloud_cover_high = Column(Float)
    dew_point_2m = Column(Float)

    # Thời điểm Bot ghi bản ghi này vào DB (thời điểm tính toán)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Bản ghi này dự báo/đại diện cho thời điểm nào?
    # - Với data quá khứ/hiện tại: forecast_for ≈ created_at
    # - Với dự báo tương lai: forecast_for = giờ tương lai cụ thể
    forecast_for = Column(DateTime, index=True)

    # Phân loại bản ghi: "historical", "current", "forecast_d1/d2/d3/d4"
    record_type = Column(String, default="current", index=True)

    # Ràng buộc duy nhất: mỗi địa điểm chỉ có 1 bản ghi cho mỗi thời điểm dự báo
    __table_args__ = (
        UniqueConstraint('location_name', 'forecast_for', name='uq_location_forecast'),
    )

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
