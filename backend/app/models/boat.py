"""
Boat and nautical equipment models.
"""

import enum
import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Float,
    Integer,
    JSON,
    Enum,
    Index,
    Numeric,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class BoatType(enum.Enum):
    """Boat equipment type enumeration."""

    BOAT = "boat"
    JET_SKI = "jet_ski"
    KAYAK = "kayak"
    PADDLEBOARD = "paddleboard"
    EQUIPMENT = "equipment"


class Boat(Base):
    """
    Boat equipment model for nautical rentals.

    Attributes:
        id: Unique identifier (UUID)
        vendor_id: Associated vendor ID
        equipment_type: Type of equipment
        brand: Brand name
        model: Model name
        year: Manufacturing year
        capacity: Maximum capacity (people)
        length_foot: Length in feet
        features: JSON dict of features
        images: JSON list of image URLs
        price_per_hour: Hourly rental price
        price_per_day: Daily rental price
        price_per_week: Weekly rental price
        requires_license: Whether boating license is required
        license_notes: Notes about license requirements
        location: Primary location
        operating_area: Operating area/water body
        rating: Average rating
        total_reviews: Number of reviews
        total_rentals: Total rentals count
        is_available: Availability status
        is_active: Active status
    """

    __tablename__ = "boats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )

    equipment_type = Column(Enum(BoatType), default=BoatType.BOAT, nullable=False)
    brand = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)

    capacity = Column(Integer, default=4)
    length_foot = Column(Float, nullable=True)

    features = Column(JSONB, default=dict)
    images = Column(JSON, default=list)

    price_per_hour = Column(Numeric(10, 2), default=0)
    price_per_day = Column(Numeric(10, 2), default=0)
    price_per_week = Column(Numeric(10, 2), default=0)

    requires_license = Column(Boolean, default=False)
    license_notes = Column(Text, nullable=True)

    location = Column(String(255), nullable=True)
    operating_area = Column(String(255), nullable=True)

    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    total_rentals = Column(Integer, default=0)

    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)

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
    vendor = relationship("Vendor", back_populates="boats")

    # Indexes for performance
    __table_args__ = (
        Index("idx_boat_vendor", "vendor_id"),
        Index("idx_boat_type", "equipment_type"),
        Index("idx_boat_available", "is_available", "is_active", "deleted_at"),
        Index("idx_boat_price", "price_per_hour"),
        Index("idx_boat_location", "location"),
        Index("idx_boat_deleted", "deleted_at"),
        # GIN index for features JSON search
        Index("idx_boat_features_gin", "features", postgresql_using="gin"),
        sa.CheckConstraint("capacity > 0", name="chk_boat_capacity_positive"),
        sa.CheckConstraint("price_per_hour >= 0", name="chk_boat_price_positive"),
    )
