"""
Super Admin User Management endpoints.
Provides comprehensive CRUD for users with audit logging.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import require_superadmin, get_password_hash
from app.core.utils import escape_like_pattern
from app.models import User, UserRole, Vendor, Booking, AuditAction
from app.services.audit_service import log_create, log_update, log_delete, AuditService

router = APIRouter()


# Request/Response Models
class UserListItem(BaseModel):
    """User item for list view."""
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    phone: Optional[str]
    avatar_url: Optional[str]
    last_login: Optional[datetime]
    created_at: datetime
    vendor_count: int
    booking_count: int


class UserDetail(BaseModel):
    """Detailed user information."""
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    avatar_url: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    failed_login_attempts: int
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    """Request to create a new user."""
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.CLIENT
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    """Request to update a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserActivityItem(BaseModel):
    """User activity log item."""
    id: str
    action: str
    entity_type: str
    entity_name: Optional[str]
    changes_summary: Optional[str]
    ip_address: Optional[str]
    created_at: datetime


# Endpoints
@router.get("", response_model=List[UserListItem])
async def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    List all users with filtering and pagination.
    """
    query = select(User)
    
    # Apply filters
    if search:
        safe_search = escape_like_pattern(search)
        search_filter = f"%{safe_search}%"
        query = query.where(
            (User.email.ilike(search_filter)) | 
            (User.full_name.ilike(search_filter))
        )
    
    if role:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if is_verified is not None:
        query = query.where(User.is_verified == is_verified)
    
    # Apply sorting
    sort_column = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Build response with counts
    response = []
    for user in users:
        # Count vendors and bookings
        vendor_count_result = await db.execute(
            select(func.count()).select_from(Vendor).where(Vendor.user_id == user.id)
        )
        vendor_count = vendor_count_result.scalar() or 0
        
        booking_count_result = await db.execute(
            select(func.count()).select_from(Booking).where(Booking.user_id == user.id)
        )
        booking_count = booking_count_result.scalar() or 0
        
        response.append({
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "vendor_count": vendor_count,
            "booking_count": booking_count,
        })
    
    return response


@router.get("/count", response_model=dict)
async def get_user_count(
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """Get total count of users with filters."""
    from sqlalchemy import func
    
    query = select(func.count(User.id))
    
    if search:
        safe_search = escape_like_pattern(search)
        search_filter = f"%{safe_search}%"
        query = query.where(
            (User.email.ilike(search_filter)) | 
            (User.full_name.ilike(search_filter))
        )
    
    if role:
        query = query.where(User.role == role)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    result = await db.execute(query)
    count = result.scalar() or 0
    
    return {"count": count}


@router.get("/{user_id}", response_model=UserDetail)
async def get_user_detail(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Get detailed information about a specific user.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "last_login": user.last_login,
        "failed_login_attempts": user.failed_login_attempts,
        "locked_until": user.locked_until,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.post("", response_model=UserDetail, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Create a new user.
    Only Super Admin can create users with admin/agent roles.
    """
    # Check if email already exists
    existing_result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    new_user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
        phone=request.phone,
        role=request.role,
        is_active=request.is_active,
        is_verified=True,  # Super Admin created users are pre-verified
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    
    db.add(new_user)
    await db.flush()
    
    # Log the action
    await log_create(
        db=db,
        user=current_user,
        entity_type="user",
        entity_id=new_user.id,
        entity_name=new_user.full_name,
        new_values={
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role.value,
            "is_active": new_user.is_active,
        },
    )
    
    await db.commit()
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "full_name": new_user.full_name,
        "phone": new_user.phone,
        "avatar_url": new_user.avatar_url,
        "role": new_user.role.value,
        "is_active": new_user.is_active,
        "is_verified": new_user.is_verified,
        "last_login": new_user.last_login,
        "failed_login_attempts": new_user.failed_login_attempts,
        "locked_until": new_user.locked_until,
        "created_at": new_user.created_at,
        "updated_at": new_user.updated_at,
    }


@router.put("/{user_id}", response_model=UserDetail)
async def update_user(
    user_id: UUID,
    request: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Update a user.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store old values for audit
    old_values = {
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }
    
    # Track what changed
    changes = []
    
    # Update fields
    if request.email is not None and request.email != user.email:
        # Check if new email is available
        existing_result = await db.execute(
            select(User).where(User.email == request.email).where(User.id != user_id)
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = request.email
        changes.append(f"email: {old_values['email']} -> {request.email}")
    
    if request.full_name is not None:
        if request.full_name != user.full_name:
            changes.append(f"full_name: {user.full_name} -> {request.full_name}")
        user.full_name = request.full_name
    
    if request.phone is not None:
        if request.phone != user.phone:
            changes.append("phone updated")
        user.phone = request.phone
    
    if request.role is not None:
        if request.role != user.role:
            changes.append(f"role: {user.role.value} -> {request.role.value}")
        user.role = request.role
    
    if request.is_active is not None:
        if request.is_active != user.is_active:
            status_text = "activated" if request.is_active else "deactivated"
            changes.append(f"account {status_text}")
        user.is_active = request.is_active
    
    if request.is_verified is not None:
        if request.is_verified != user.is_verified:
            changes.append(f"verification: {user.is_verified} -> {request.is_verified}")
        user.is_verified = request.is_verified
    
    user.updated_at = datetime.now(timezone.utc)
    
    await db.flush()
    
    # Log the action
    new_values = {
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }
    
    await log_update(
        db=db,
        user=current_user,
        entity_type="user",
        entity_id=user.id,
        entity_name=user.full_name,
        old_values=old_values,
        new_values=new_values,
        changes_summary=f"Updated user: {', '.join(changes)}" if changes else "No changes made",
    )
    
    await db.commit()
    
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "last_login": user.last_login,
        "failed_login_attempts": user.failed_login_attempts,
        "locked_until": user.locked_until,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.delete("/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Delete a user permanently.
    This action cannot be undone.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot delete yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Cannot delete other super_admins
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete Super Admin accounts"
        )
    
    # Store data for audit before deletion
    old_values = {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "created_at": user.created_at.isoformat(),
    }
    
    entity_name = user.full_name
    
    # Delete user
    await db.delete(user)
    await db.flush()
    
    # Log the action
    await log_delete(
        db=db,
        user=current_user,
        entity_type="user",
        entity_id=user_id,
        entity_name=entity_name,
        old_values=old_values,
    )
    
    await db.commit()


@router.get("/{user_id}/activity", response_model=List[UserActivityItem])
async def get_user_activity(
    user_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Get activity history for a specific user.
    """
    from app.models import AuditLog
    
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.user_id == user_id)
        .order_by(desc(AuditLog.created_at))
        .offset(offset)
        .limit(limit)
    )
    
    logs = result.scalars().all()
    
    return [
        {
            "id": str(log.id),
            "action": log.action.value,
            "entity_type": log.entity_type,
            "entity_name": log.entity_name,
            "changes_summary": log.changes_summary,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.post("/{user_id}/impersonate", response_model=dict)
async def impersonate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Generate an impersonation token to log in as another user.
    This is audited and should be used carefully.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot impersonate super admins
    if target_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot impersonate Super Admin accounts"
        )
    
    # Cannot impersonate inactive users
    if not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot impersonate inactive users"
        )
    
    # Log the impersonation attempt
    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.IMPERSONATE,
        entity_type="user",
        entity_id=target_user.id,
        entity_name=target_user.full_name,
        changes_summary=f"Started impersonating user: {target_user.email}",
    )
    
    await db.commit()
    
    # Generate a special impersonation token
    from app.core.security import create_access_token
    
    impersonation_token = create_access_token(
        subject=str(target_user.id),
        expires_delta=timedelta(hours=1)  # Short-lived token
    )
    
    return {
        "message": f"Impersonating user: {target_user.full_name}",
        "target_user": {
            "id": str(target_user.id),
            "email": target_user.email,
            "full_name": target_user.full_name,
            "role": target_user.role.value,
        },
        "impersonation_token": impersonation_token,
        "expires_in": "1 hour",
        "warning": "This action has been logged. Use with caution.",
    }


@router.post("/{user_id}/block", response_model=dict)
async def block_user(
    user_id: UUID,
    reason: str = Query(..., max_length=500, description="Reason for blocking"),
    duration_hours: Optional[int] = Query(None, description="Block duration in hours (null for permanent)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Block/suspend a user account.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot block Super Admin accounts"
        )
    
    user.is_active = False
    
    if duration_hours:
        user.locked_until = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
    else:
        user.locked_until = None  # Permanent
    
    await db.flush()
    
    # Log the action
    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.SUSPEND,
        entity_type="user",
        entity_id=user.id,
        entity_name=user.full_name,
        changes_summary=f"User blocked: {reason}. Duration: {duration_hours} hours" if duration_hours else f"User permanently blocked: {reason}",
        metadata={"reason": reason, "duration_hours": duration_hours},
    )
    
    await db.commit()
    
    return {
        "message": f"User {user.email} has been blocked",
        "reason": reason,
        "duration_hours": duration_hours,
        "is_permanent": duration_hours is None,
    }


@router.post("/{user_id}/unblock", response_model=dict)
async def unblock_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Unblock/reactivate a user account.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    user.locked_until = None
    user.failed_login_attempts = 0
    
    await db.flush()
    
    # Log the action
    from app.services.audit_service import AuditService
    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.ACTIVATE,
        entity_type="user",
        entity_id=user.id,
        entity_name=user.full_name,
        changes_summary="User account unblocked/reactivated",
    )
    
    await db.commit()
    
    return {
        "message": f"User {user.email} has been unblocked",
    }


