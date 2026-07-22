# src/s2_booking/config.py
import os
from dotenv import load_dotenv

load_dotenv()


JWT_SECRET    = os.getenv("JWT_SECRET", "changeme-set-a-real-secret-in-dotenv")
JWT_ALGORITHM = "HS256"

# Toggle: True khi S3 chưa chạy, False khi tích hợp thật
MOCK_AUTH = os.getenv("MOCK_AUTH", "false").lower() == "true"
DATABASE_URL  = os.getenv("S2_DATABASE_URL", "sqlite:///./s2_booking.db")

