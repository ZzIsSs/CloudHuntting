# src/s2_booking/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dataclasses import dataclass
from . import config

# tokenUrl trỏ về S3 — để Swagger UI biết lấy token ở đâu
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8003/auth/login")


@dataclass
class CurrentUser:
    id: int    # int(sub) — S3 encode sub=str(user.id)
    role: str  # "user" | "admin" | "moderator"


# Mock tokens dùng khi MOCK_AUTH=true
_MOCK_TOKENS: dict[str, CurrentUser] = {
    "dev-token-user":    CurrentUser(id=1,   role="user"),
    "dev-token-moderator": CurrentUser(id=100, role="moderator"),
    "dev-token-admin":   CurrentUser(id=999, role="admin"),
}


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> CurrentUser:
    """
    Decode JWT từ S3.
    S3 tạo token: jwt.encode({"sub": str(user.id), "role": user.role.value}, JWT_SECRET, HS256)
    S2 decode:    jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    Không cần gọi HTTP sang S3 — dùng chung JWT_SECRET là đủ.
    """
    if config.MOCK_AUTH:
        if token not in _MOCK_TOKENS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mock token không hợp lệ. Dùng: dev-token-user | dev-token-admin",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return _MOCK_TOKENS[token]

    # JWT thật
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token thiếu trường 'sub'",
        )

    return CurrentUser(id=int(sub), role=payload.get("role", "user"))