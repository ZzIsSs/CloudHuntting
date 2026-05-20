import os
from dotenv import load_dotenv

load_dotenv()  # nạp .env

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30