"""
Base model and shared enums for all database models.
This module provides the declarative base and common enums used across the application.
"""

import enum
from app.core.database import Base

# Re-export Base from database module
__all__ = ["Base", "UserRole", "VendorStatus", "BookingStatus", "BlogPostStatus"]


class UserRole(str, enum.Enum):
    """User role enumeration for access control."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    AGENT = "agent"
    CUSTOMER_SERVICE = "customer_service"
    VENDOR = "vendor"
    CLIENT = "client"


class VendorStatus(str, enum.Enum):
    """Vendor account status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class BookingStatus(str, enum.Enum):
    """Booking status enumeration for lifecycle management."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"


class BlogPostStatus(str, enum.Enum):
    """Blog post publication status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class TourType(str, enum.Enum):
    """Tour type enumeration for categorization."""

    ADVENTURE = "adventure"
    CULTURAL = "cultural"
    NATURE = "nature"
    WILDLIFE = "wildlife"
    GASTRONOMIC = "gastronomic"
    BEACH = "beach"
