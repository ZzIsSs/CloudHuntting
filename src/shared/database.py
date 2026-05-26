import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DB file path in the shared directory
DB_PATH = os.path.join(os.path.dirname(__file__), "shared_cloud_hunting.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
