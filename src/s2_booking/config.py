# src/s2_booking/config.py
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET    = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
DATABASE_URL = os.getenv("S2_DATABASE_URL", "sqlite:///./s2_booking.db")
MOCK_AUTH = os.getenv("MOCK_AUTH", "true").lower() == "true"
