# src/s2_booking/config.py
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET    = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
DATABASE_URL = os.getenv("S2_DATABASE_URL", "sqlite:///./s2_booking.db")
MOCK_AUTH = os.getenv("MOCK_AUTH", "true").lower() == "true"

# Quy tắc đặt chỗ
CANCEL_WINDOW_HOURS    = int(os.getenv("CANCEL_WINDOW_HOURS", "2"))
MAX_BOOKING_DAYS_AHEAD = int(os.getenv("MAX_BOOKING_DAYS_AHEAD", "30"))