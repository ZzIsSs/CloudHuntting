from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, auth
from shared.database import get_db  # dependency lấy session DB

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # kiểm tra username/email đã tồn tại chưa...
    hashed = auth.hash_password(user_in.password)
    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if not user or not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập")
    access_token = auth.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}