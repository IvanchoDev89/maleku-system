import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models import User, UserRole
from app.schemas import (
    UserResponse, UserUpdate, PaginationParams, PaginatedResponse
)

router = APIRouter()

class DeleteResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str


class MarkReadResponse(BaseModel):
    message: str
    conversation_id: str


class ReorderResponse(BaseModel):
    message: str
    items_updated: int


class ActivateResponse(BaseModel):
    message: str
    is_active: bool


class ChangeRoleResponse(BaseModel):
    message: str
    user_id: str
    new_role: str


class VerifyResponse(BaseModel):
    message: str
    is_verified: bool


class ToggleActiveResponse(BaseModel):
    message: str
    is_active: bool


class PresignedUrlResponse(BaseModel):
    url: str
    expires_in: int
    fields: dict



@router.get("", response_model=PaginatedResponse)
async def get_users(
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    # Count total
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar()
    
    # Get users with pagination
    offset = (params.page - 1) * params.page_size
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(params.page_size)
    )
    users = result.scalars().all()
    
    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total,
        has_prev=params.page > 1
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Users can only see their own profile unless admin
    if current_user.role != UserRole.SUPER_ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user data"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if data.full_name:
        user.full_name = data.full_name
    if data.phone:
        user.phone = data.phone
    if data.avatar_url:
        user.avatar_url = data.avatar_url
    
    await db.flush()
    await db.commit()
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    await db.flush()
    await db.commit()
    
    return {"message": "User deactivated"}


@router.post("/{user_id}/activate", response_model=ActivateResponse)
async def activate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    await db.flush()
    await db.commit()
    
    return {"message": "User activated"}


@router.post("/{user_id}/role", response_model=ChangeRoleResponse)
async def change_user_role(
    user_id: uuid.UUID,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        user.role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    await db.flush()
    await db.commit()
    
    return {"message": f"User role changed to {role}"}