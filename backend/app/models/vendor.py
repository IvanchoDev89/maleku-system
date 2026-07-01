"""
Vendor model and related schemas.
Represents business vendors offering properties, tours, and services.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Float,
    Integer,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, column_property
from sqlalchemy import select as sa_select, func as sa_func

from app.models.booking import Booking
from app.models.base import Base, VendorStatus


class Vendor(Base):
    """
    Vendor model representing business partners on the platform.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Associated user account ID
        business_name: Legal business name
        business_slug: URL-friendly identifier
        business_type: Type of business (hotel, tour operator, etc.)
        tax_id: Tax identification number
        description: Business description
        logo_url: Business logo URL
        cover_image: Cover image URL
        address: Physical address
        phone: Contact phone
        email: Contact email
        rating: Average rating (0-5)
        total_reviews: Number of reviews received
        commission_rate: Platform commission percentage
        stripe_account_id: Stripe Connect account ID
        stripe_connected: Whether Stripe account is connected
        is_verified: Whether vendor is verified
        is_active: Whether vendor account is active
        is_featured: Whether vendor is featured
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    business_name = Column(String(255), nullable=False)
    business_slug = Column(String(255), unique=True, index=True, nullable=False)
    business_type = Column(String(50), nullable=False)
    tax_id = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    cover_image = Column(String(500), nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    commission_rate = Column(Numeric(5, 2), default=0.10)
    stripe_account_id = Column(String(255), nullable=True)
    stripe_connected = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default=VendorStatus.PENDING.value, nullable=False)

    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="vendor", uselist=False)
    properties = relationship("Property", back_populates="vendor")
    tours = relationship("Tour", back_populates="vendor")
    bookings = relationship("Booking", back_populates="vendor")
    vehicles = relationship("Vehicle", back_populates="vendor")
    boats = relationship("Boat", back_populates="vendor")
    flights = relationship("Flight", back_populates="vendor")
    transportation = relationship("Transportation", back_populates="vendor")
    conversations = relationship("Conversation", back_populates="participant_vendor")

    total_bookings = column_property(
        sa_select(sa_func.count(Booking.id))
        .where(Booking.vendor_id == id)
        .correlate_except(Booking)
        .scalar_subquery()
    )

    __table_args__ = (
        Index("idx_vendor_user", "user_id"),
        Index("idx_vendor_slug", "business_slug"),
        Index("idx_vendor_verified", "is_verified"),
        Index("idx_vendor_active", "is_active"),
        Index("idx_vendor_featured", "is_featured"),
        Index("idx_vendor_business_type", "business_type"),
        Index("idx_vendor_created_at", "created_at"),
    )
