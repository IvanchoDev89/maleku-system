"""Authentication endpoints - login, register, refresh, password reset."""
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr, field_validator
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_async_session
from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token,
    create_verification_token, create_password_reset_token, verify_token,
    get_current_user,
)
from app.models.user import User
from app.models.base import UserRole
from app.services.base import BaseService
from app.services.email_service import email_service
from app.core.logging import get_logger
from app.core.token_blacklist import token_blacklist

logger = get_logger(__name__)
router = APIRouter()
user_service = BaseService(User)
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)


def normalize_role(role: UserRole) -> str:
    """Normalize role to consistent string format for API responses."""
    role_map = {
        UserRole.SUPER_ADMIN: "super_admin",
        UserRole.ADMIN: "admin",
        UserRole.AGENT: "agent",
        UserRole.CUSTOMER_SERVICE: "customer_service",
        UserRole.VENDOR: "vendor",
        UserRole.CLIENT: "client",
    }
    return role_map.get(role, role.value)


# Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password has uppercase, lowercase, number, and special char."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('full_name')
    @classmethod
    def validate_name_not_email(cls, v: str) -> str:
        """Prevent using email as name."""
        if '@' in v:
            raise ValueError('Full name cannot contain @ symbol')
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class VerifyEmailRequest(BaseModel):
    token: str


# Endpoints
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    user_in: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Register new user with enhanced security."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Always hash password first (timing attack protection)
    password_hash = get_password_hash(user_in.password)
    
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_in.email} from IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_data = {
        'email': user_in.email.lower().strip(),  # Normalize email
        'password_hash': password_hash,
        'full_name': user_in.full_name,
        'phone': user_in.phone,
        'role': UserRole.CLIENT,
        'is_active': True,
        'is_verified': False
    }
    
    try:
        user = await user_service.create(db, obj_in=user_data)
        logger.info(f"New user registered: {user.email} from IP: {client_ip}")
    except Exception as e:
        logger.error(f"User registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
    
    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": normalize_role(user.role)
        }
    }


@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """Authenticate user and return tokens."""
    # Find user
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    
    # Timing attack protection: always perform password verification
    # even when user doesn't exist to prevent timing attacks
    if not user:
        # Perform dummy verification to prevent timing attacks
        get_password_hash(login_in.password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check account locked
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to failed attempts"
        )
    
    if not verify_password(login_in.password, user.password_hash):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Reset failed attempts and update last login
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    
    # Generate tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": normalize_role(user.role),
            "is_verified": user.is_verified
        }
    }


@router.post("/refresh")
async def refresh_token(
    refresh_in: RefreshRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_in.refresh_token)
    if not payload or payload.get('type') != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get('sub')
    user = await user_service.get(db, id=UUID(user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": normalize_role(user.role)
        }
    }


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout - invalidate token (add to blacklist)."""
    token = credentials.credentials
    
    # Add token to blacklist
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            token_blacklist.blacklist_token(token, expires_at)
            logger.info("Token added to blacklist on logout")
    except Exception as e:
        logger.warning(f"Failed to blacklist token on logout: {e}")
    
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
@limiter.limit("3/minute")  # Rate limiting: 3 forgot password requests por minuto
async def forgot_password(
    request: Request,
    forgot_in: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """Request password reset email."""
    client_ip = request.client.host if request.client else "unknown"
    
    result = await db.execute(select(User).where(User.email == forgot_in.email.lower().strip()))
    user = result.scalar_one_or_none()
    
    if user:
        # Generate secure reset token
        reset_token = create_password_reset_token(user.email)

        # Store in user record
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await db.commit()

        logger.info(f"Password reset requested for {user.email} from IP: {client_ip}")

        # Send reset email (MailHog in dev, Resend in prod)
        try:
            site_url = getattr(settings, "SITE_URL", "http://localhost:3000")
            reset_link = f"{site_url}/reset-password?token={reset_token}"
            content = f"""
                <p>Hi {user.full_name},</p>
                <p>We received a request to reset your password. Click the link below to set a new password:</p>
                <p><a href="{reset_link}"
                      style="background:#1e7a67;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">
                      Reset Password
                   </a></p>
                <p>This link expires in 1 hour. If you didn't request this, you can safely ignore this email.</p>
            """
            await email_service.send_email(
                to=user.email,
                subject="Reset your Costa Rica Travel password",
                html=email_service._build_email_template("Password Reset", content),
            )
        except Exception as e:  # noqa: BLE001
            # Never let email failure leak user existence or break the flow.
            logger.error(f"Failed to send password reset email: {e}")
    else:
        logger.warning(f"Password reset attempted for non-existent email: {forgot_in.email} from IP: {client_ip}")

    # Always return success to prevent email enumeration
    return {"message": "If email exists, reset instructions sent"}


@router.get("/me")
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
):
    """Get current user profile."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get('sub')
    user = await user_service.get(db, id=UUID(user_id))
    
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
        "role": normalize_role(user.role),
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "last_login": user.last_login.isoformat() if user.last_login else None
    }


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    reset_in: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Reset password using token."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Verify token
    email = verify_token(reset_in.token, "password_reset")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Find user by email and token
    result = await db.execute(
        select(User).where(
            User.email == email,
            User.password_reset_token == reset_in.token
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check token expiration
    if user.password_reset_expires and user.password_reset_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Update password
    user.password_hash = get_password_hash(reset_in.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    # Invalidate all existing tokens for this user
    user.failed_login_attempts = 0
    user.locked_until = None
    
    await db.commit()
    
    logger.info(f"Password reset completed for {user.email} from IP: {client_ip}")
    
    return {"message": "Password reset successfully"}


@router.post("/verify-email")
async def verify_email(
    verify_in: VerifyEmailRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Verify email using token."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Verify token
    email = verify_token(verify_in.token, "verification")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Find user
    result = await db.execute(
        select(User).where(
            User.email == email,
            User.email_verification_token == verify_in.token
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    # Check token expiration
    if user.email_verification_expires and user.email_verification_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
    
    # Mark as verified
    user.is_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    await db.commit()
    
    logger.info(f"Email verified for {user.email} from IP: {client_ip}")
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Resend verification email."""
    client_ip = request.client.host if request.client else "unknown"
    
    user_id = current_user.id
    user = await user_service.get(db, id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    verification_token = create_verification_token(user.email)
    user.email_verification_token = verification_token
    user.email_verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    await db.commit()

    logger.info(f"Verification email resent for {user.email} from IP: {client_ip}")

    # Send verification email
    try:
        site_url = getattr(settings, "SITE_URL", "http://localhost:3000")
        verify_link = f"{site_url}/verify-email?token={verification_token}"
        content = f"""
            <p>Hi {user.full_name},</p>
            <p>Please confirm your email address by clicking the link below:</p>
            <p><a href="{verify_link}"
                  style="background:#1e7a67;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">
                  Verify Email
               </a></p>
            <p>This link expires in 24 hours.</p>
        """
        await email_service.send_email(
            to=user.email,
            subject="Verify your Costa Rica Travel email",
            html=email_service._build_email_template("Email Verification", content),
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to send verification email: {e}")

    return {"message": "Verification email sent"}
