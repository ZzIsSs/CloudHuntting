# src/s2_booking/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# JWT — đọc từ .env, phải khớp hệt với S3
JWT_SECRET    = os.getenv("JWT_SECRET", "changeme-set-a-real-secret-in-dotenv")
JWT_ALGORITHM = "HS256"

# Toggle: True khi S3 chưa chạy, False khi tích hợp thật
MOCK_AUTH = os.getenv("MOCK_AUTH", "false").lower() == "true"

# Quy tắc đặt chỗ
CANCEL_WINDOW_HOURS    = int(os.getenv("CANCEL_WINDOW_HOURS", "2"))
MAX_BOOKING_DAYS_AHEAD = int(os.getenv("MAX_BOOKING_DAYS_AHEAD", "30"))