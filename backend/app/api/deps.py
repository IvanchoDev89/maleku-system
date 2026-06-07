"""
API dependencies — dict-based auth with full security checks.

Returns a dict (not ORM object) for backward compatibility with
34+ call sites using current_user.get('sub') style access.
"""
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.core.token_blacklist import token_blacklist
from app.models.user import User
from app.models.base import UserRole

# Re-export security scheme so callers can use Depends(security)
from app.core.security import security


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    token = credentials.credentials

    if token_blacklist.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    issued_at = payload.get("iat")
    if issued_at and token_blacklist.is_user_tokens_blacklisted(
        user_id, datetime.fromtimestamp(issued_at, tz=timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    payload["role"] = user.role.value if hasattr(user.role, 'value') else user.role
    payload["is_active"] = user.is_active
    payload["is_verified"] = user.is_verified
    payload["email"] = user.email
    payload["full_name"] = user.full_name

    return payload


def require_role(*roles: UserRole):
    allowed = {r.value if hasattr(r, 'value') else r for r in roles}
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get("role") not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {', '.join(allowed)}"
            )
        return current_user
    return role_checker


require_admin = require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN)

require_vendor = require_role(
    UserRole.VENDOR, UserRole.ADMIN, UserRole.SUPER_ADMIN
)


async def require_superadmin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != UserRole.SUPER_ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Super Admin access required."
        )
    return current_user
