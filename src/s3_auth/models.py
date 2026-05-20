from sqlalchemy import Column, Integer, String, Enum
from shared.database import Base  # cần có Base từ shared
import enum

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    # ... thêm các trường khác nếu cần