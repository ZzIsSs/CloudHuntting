import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Lấy đường dẫn tuyệt đối của thư mục chứa file database.py hiện tại
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
S6_DB_URL = f"sqlite:///{os.path.join(BASE_DIR, 's6_preferences.db')}"

engine = create_engine(
    S6_DB_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class UserPreferenceLog(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    start_time = Column(String)
    max_distance_km = Column(Float)
    travel_style = Column(String)
    preferred_vibe = Column(String)
    vehicle_type = Column(String)

class NotificationLog(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)
    message = Column(String)
    probability = Column(Integer)
    timestamp = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
