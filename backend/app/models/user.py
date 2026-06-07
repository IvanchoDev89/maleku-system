"""
User model and related schemas.
Handles user accounts, authentication, and profile data.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, UserRole


class User(Base):
    """
    User model representing registered users of the platform.
    
    Attributes:
        id: Unique identifier (UUID)
        email: User's email address (unique)
        password_hash: Hashed password for authentication
        full_name: User's full name
        phone: Optional phone number
        avatar_url: URL to profile image
        role: User role for access control
        is_active: Whether the account is active
        is_verified: Whether email is verified
        email_verification_token: Token for email verification
        email_verification_expires: Expiration time for verification token
        password_reset_token: Token for password reset
        password_reset_expires: Expiration time for reset token
        last_login: Last successful login timestamp
        failed_login_attempts: Count of consecutive failed login attempts
        locked_until: Account lockout expiration time
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Email verification fields
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset fields
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Security tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_role_active', 'role', 'is_active', 'deleted_at'),
        Index('idx_user_created', 'created_at'),
        Index('idx_user_deleted', 'deleted_at'),
    )
    
    # Relationships
    vendor = relationship("Vendor", back_populates="user", uselist=False)
    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    blog_posts = relationship("BlogPost", back_populates="author")
    conversations = relationship("Conversation", back_populates="participant_user")
    # Messages uses polymorphic sender (user/vendor/system) - no direct FK
    messages = relationship("Message", primaryjoin="User.id == foreign(Message.sender_id)", viewonly=True)
    
    # Audit and security logging
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    security_logs = relationship("SecurityLog", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    
    # Marketing and email
    email_preferences = relationship("EmailPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    inbox_messages = relationship("InboxMessage", foreign_keys="InboxMessage.customer_id", back_populates="customer", lazy="dynamic", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", foreign_keys="EmailLog.recipient_id", back_populates="recipient", lazy="dynamic")
