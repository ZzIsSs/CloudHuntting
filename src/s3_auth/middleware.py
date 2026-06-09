from fastapi import Depends, HTTPException, status
from .dependencies import get_current_user
from .models import RoleEnum


def role_required(allowed_roles: list[RoleEnum]):
    async def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập",
            )
        return current_user
    return role_checker


# Shortcut dùng trực tiếp trong Depends()
admin_required = role_required([RoleEnum.admin])
moderator_required = role_required([RoleEnum.admin, RoleEnum.moderator])
