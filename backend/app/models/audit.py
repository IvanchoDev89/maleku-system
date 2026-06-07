"""
Audit and logging models for comprehensive system monitoring.
Tracks all actions, security events, and system changes.
"""
import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Index, desc, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditAction(str, PyEnum):
    """Enumeration of possible audit actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    ACTIVATE = "activate"
    IMPERSONATE = "impersonate"
    PASSWORD_CHANGE = "password_change"
    ROLE_CHANGE = "role_change"
    SETTINGS_CHANGE = "settings_change"
    VIEW = "view"
    SEARCH = "search"
    DOWNLOAD = "download"
    SHARE = "share"
    COMMENT = "comment"
    RATE = "rate"
    PAYMENT = "payment"
    REFUND = "refund"
    CANCEL = "cancel"
    CONFIRM = "confirm"
    COMPLETE = "complete"


class SecurityAction(str, PyEnum):
    """Enumeration of security-related actions."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    ACCESS_DENIED = "access_denied"
    RATE_LIMIT_HIT = "rate_limit_hit"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFICATION = "mfa_verification"
    SESSION_EXPIRED = "session_expired"
    FORCE_LOGOUT = "force_logout"


class AuditLog(Base):
    """
    Comprehensive audit log for all system actions.
    Tracks who did what, when, and from where.
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User information
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    user_email = Column(String(255), nullable=True)  # Snapshot in case user is deleted
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # user, vendor, property, booking, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    entity_name = Column(String(255), nullable=True)  # Human-readable identifier
    
    # Data snapshots (for tracking changes)
    old_values = Column(JSONB, nullable=True)  # Previous state
    new_values = Column(JSONB, nullable=True)  # New state
    changes_summary = Column(Text, nullable=True)  # Human-readable summary of changes
    
    # Request context
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True, index=True)  # For correlating with API logs
    
    # Additional metadata
    session_id = Column(String(100), nullable=True)
    correlation_id = Column(String(100), nullable=True, index=True)  # For tracing across services
    extra_data = Column(JSONB, nullable=True)  # Flexible additional data
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs", lazy="selectin")
    
    # Indexes for common queries
    __table_args__ = (
        Index("ix_audit_logs_user_action", "user_id", "action"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_created_at_desc", desc("created_at")),
        Index("ix_audit_logs_action_entity_created", "action", "entity_type", "created_at"),
    )


class SecurityLog(Base):
    """
    Security-focused logging for authentication and access control events.
    Separate from audit logs for easier security monitoring and alerting.
    """
    __tablename__ = "security_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User information (nullable for failed login attempts)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True, index=True)  # Email used in login attempt
    
    # Security action
    action = Column(Enum(SecurityAction), nullable=False, index=True)
    
    # Action details
    description = Column(Text, nullable=True)  # Human-readable description
    severity = Column(String(20), default="info")  # info, warning, critical
    
    # Context data (stored as JSON for flexibility)
    details = Column(JSONB, nullable=True)  # {
    #     "reason": "invalid_password",
    #     "attempt_count": 3,
    #     "lockout_duration": 300,
    #     "mfa_method": "totp",
    #     "mfa_success": True,
    #     "previous_ip": "192.168.1.1",
    #     "password_age_days": 45,
    #     ...
    # }
    
    # Request context
    ip_address = Column(INET, nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    country_code = Column(String(2), nullable=True)  # GeoIP country
    city = Column(String(100), nullable=True)  # GeoIP city
    
    # Device fingerprinting (for detecting unusual access patterns)
    device_fingerprint = Column(String(64), nullable=True, index=True)
    
    # Session information
    session_id = Column(String(100), nullable=True, index=True)
    token_id = Column(String(100), nullable=True)  # JWT token identifier
    
    # Additional metadata
    request_id = Column(String(100), nullable=True)
    correlation_id = Column(String(100), nullable=True)
    extra_data = Column(JSONB, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="security_logs", lazy="selectin")
    
    # Indexes for security monitoring queries
    __table_args__ = (
        Index("ix_security_logs_user_action", "user_id", "action"),
        Index("ix_security_logs_ip_action", "ip_address", "action"),
        Index("ix_security_logs_created_at_desc", desc("created_at")),
        Index("ix_security_logs_failed_logins", "action", "created_at"),  # For detecting brute force
        Index("ix_security_logs_suspicious", "severity", "created_at"),  # For alerting
    )


class RolePermission(Base):
    """
    Granular role-based access control (RBAC) configuration.
    Defines what each role can do on each module.
    """
    __tablename__ = "role_permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Role identification
    role = Column(String(50), nullable=False, index=True)  # super_admin, admin, agent, etc.
    
    # Module/Resource
    module = Column(String(50), nullable=False, index=True)  # users, vendors, bookings, etc.
    
    # Permissions (stored as array of strings)
    permissions = Column(JSONB, nullable=False, default=list)  # ["create", "read", "update", "delete", "approve", "manage"]
    
    # Additional constraints
    conditions = Column(JSONB, nullable=True)  # Conditional permissions, e.g., {"own_data_only": True}
    
    # Metadata
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Unique constraint: one permission set per role per module
    __table_args__ = (
        Index("ix_role_permissions_role_module", "role", "module", unique=True),
    )


class PointOfSale(Base):
    """
    Physical point of sale terminals for in-person bookings.
    Allows admins/agents to process bookings at physical locations.
    """
    __tablename__ = "points_of_sale"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)  # Short code for receipts
    location = Column(String(255), nullable=True)  # Physical address
    description = Column(Text, nullable=True)
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Configuration
    settings = Column(JSONB, nullable=True)  # {
    #     "receipt_prefix": "POS-001",
    #     "auto_print": True,
    #     "currency": "USD",
    #     "tax_rate": 0.13,
    #     "commission_rate": 0.05,
    #     "allowed_payment_methods": ["cash", "card", "transfer"],
    #     "receipt_template": "default",
    #     ...
    # }
    
    # Security
    api_key_hash = Column(String(255), nullable=True)  # Hashed API key for POS authentication
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    assigned_user = relationship("User", lazy="selectin")
    
    # Indexes
    __table_args__ = (
        Index("ix_points_of_sale_active", "is_active"),
        Index("ix_points_of_sale_assigned", "assigned_to"),
    )
