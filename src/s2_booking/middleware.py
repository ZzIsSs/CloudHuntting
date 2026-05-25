# src/s2_booking/middleware.py
"""
Middleware chứa các dependency kiểm tra role, quyền hạn của user.
"""
from fastapi import Depends, HTTPException, status
from .dependencies import get_current_user, CurrentUser


def role_required(*allowed_roles: str):
    """
    Factory tạo dependency kiểm tra role.

    Dùng trong router:
        Depends(role_required("user"))
        Depends(role_required("admin", "moderator"))
    """
    async def role_checker(
        current_user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Chức năng này yêu cầu quyền: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# Shortcut — dùng trực tiếp trong router như S3 dùng admin_required
user_required      = role_required("user", "admin", "moderator")
moderator_required = role_required("admin", "moderator")
admin_required     = role_required("admin")