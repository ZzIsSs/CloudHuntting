# src/s2_booking/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from jose import jwt, JWTError
from dataclasses import dataclass
from . import config


# Swagger sẽ dùng Bearer token
security = HTTPBearer()


@dataclass
class CurrentUser:
    """Thông tin user sau khi decode JWT."""
    id: int
    role: str


# ── Mock tokens dùng khi MOCK_AUTH=true ──────────────────────────────
_MOCK_TOKENS: dict[str, CurrentUser] = {
    "dev-token-user": CurrentUser(id=1, role="user"),
    "dev-token-partner": CurrentUser(id=100, role="moderator"),
    "dev-token-admin": CurrentUser(id=999, role="admin"),
}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:

    token = credentials.credentials

    # ── Dev mode: dùng mock token ────────────────────────────────────
    if config.MOCK_AUTH:
        if token not in _MOCK_TOKENS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Mock token không hợp lệ",
            )

        return _MOCK_TOKENS[token]

    # ── JWT mode thật ────────────────────────────────────────────────
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
            detail="Token thiếu thông tin người dùng",
        )

    return CurrentUser(
        id=int(sub),
        role=payload.get("role", "user")
    )