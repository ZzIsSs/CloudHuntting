from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import auth, models
from src.shared.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

import os
from dotenv import load_dotenv

load_dotenv()

# ── Bật/tắt xác thực tại đây ──────────────────────────────────────────────
BYPASS_AUTH = os.getenv("MOCK_AUTH", "true").lower() == "true"   # True = bỏ qua auth | False = bật lại auth bình thường
# ─────────────────────────────────────────────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:

    if BYPASS_AUTH:
        # Trả về mock user admin, không cần DB, không cần token
        mock = models.User()
        mock.id       = 0
        mock.username = "dev"
        mock.email    = "dev@local"
        mock.role     = models.RoleEnum.admin
        return mock

    # ── Auth thật từ đây trở xuống ────────────────────────────────────────
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = auth.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    raw_sub = payload.get("sub")
    if raw_sub is None:
        raise credentials_exception

    try:
        user_id = int(raw_sub)
    except (ValueError, TypeError):
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng không tồn tại",
        )
    return user