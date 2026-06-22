"""
Vehicle model for car rental marketplace.
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


class VehicleType(str, enum.Enum):
    """Vehicle type enumeration."""

    CAR = "car"
    SUV = "suv"
    VAN = "van"
    MINIBUS = "minibus"
    MOTORCYCLE = "motorcycle"


class TransmissionType(str, enum.Enum):
    """Transmission type enumeration."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"


class FuelType(str, enum.Enum):
    """Fuel type enumeration."""

    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class Vehicle(Base):
    """
    Vehicle model for car rental listings.

    Attributes:
        id: Unique identifier (UUID)
        vendor_id: Associated vendor ID
        vehicle_type: Type of vehicle (car, suv, van, etc.)
        brand: Vehicle brand
        model: Vehicle model
        year: Manufacturing year
        transmission: Transmission type
        fuel_type: Fuel type
        seats: Number of seats
        license_plate: License plate number
        color: Vehicle color
        mileage: Current mileage
        features: JSON dict of features (ac, wifi, bluetooth, etc.)
        images: JSON list of image URLs
        price_per_day: Daily rental price
        price_per_week: Weekly rental price
        price_per_month: Monthly rental price
        insurance_options: JSON dict of insurance options
        deposit_amount: Security deposit amount
        location: Primary location
        pickup_locations: JSON list of pickup locations
        dropoff_locations: JSON list of dropoff locations
        requirements: JSON list of rental requirements
        rating: Average rating
        total_reviews: Number of reviews
        total_rentals: Total rentals count
        is_available: Availability status
        is_active: Active status
    """

    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )

    vehicle_type = Column(Enum(VehicleType), default=VehicleType.CAR, nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    transmission = Column(Enum(TransmissionType), default=TransmissionType.AUTOMATIC)
    fuel_type = Column(Enum(FuelType), default=FuelType.GASOLINE)
    seats = Column(Integer, default=5)

    license_plate = Column(String(20), nullable=True)
    color = Column(String(30), nullable=True)
    mileage = Column(Integer, default=0)

    features = Column(JSONB, default=dict)
    images = Column(JSON, default=list)

    price_per_day = Column(Numeric(10, 2), default=0)
    price_per_week = Column(Numeric(10, 2), default=0)
    price_per_month = Column(Numeric(10, 2), default=0)

    insurance_options = Column(JSON, default=dict)
    deposit_amount = Column(Numeric(10, 2), default=0)

    location = Column(String(255), nullable=True)
    pickup_locations = Column(JSON, default=list)
    dropoff_locations = Column(JSON, default=list)

    requirements = Column(JSON, default=list)

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
    vendor = relationship("Vendor", back_populates="vehicles")

    # Indexes for performance
    __table_args__ = (
        Index("idx_vehicle_vendor", "vendor_id"),
        Index("idx_vehicle_is_active", "is_active"),
        Index("idx_vehicle_is_available", "is_available"),
        Index("idx_vehicle_created_at", "created_at"),
        Index("idx_vehicle_type", "vehicle_type"),
        Index("idx_vehicle_available", "is_available", "is_active", "deleted_at"),
        Index("idx_vehicle_price", "price_per_day"),
        Index("idx_vehicle_location", "location"),
        Index("idx_vehicle_deleted", "deleted_at"),
        # GIN index for features JSON search
        Index("idx_vehicle_features_gin", "features", postgresql_using="gin"),
        sa.CheckConstraint(
            "year >= 1900 AND year <= 2100", name="chk_vehicle_year_range"
        ),
        sa.CheckConstraint("seats > 0", name="chk_vehicle_seats_positive"),
        sa.CheckConstraint("price_per_day >= 0", name="chk_vehicle_price_positive"),
    )
