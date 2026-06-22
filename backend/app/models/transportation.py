"""
Transportation model for private transport services.
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


class TransportServiceType(str, enum.Enum):
    """Transportation service type enumeration."""

    AIRPORT_TRANSFER = "airport_transfer"
    CITY_TOUR = "city_tour"
    CUSTOM_ROUTE = "custom_route"


class TransportVehicleType(str, enum.Enum):
    """Transport vehicle type enumeration."""

    SEDAN = "sedan"
    VAN = "van"
    MINIBUS = "minibus"
    BUS = "bus"


class PricingType(str, enum.Enum):
    """Pricing model enumeration."""

    PER_DAY = "per_day"
    PER_HOUR = "per_hour"
    PER_KM = "per_km"
    PER_ROUTE = "per_route"


class DayType(str, enum.Enum):
    """Day type enumeration for pricing."""

    WEEKDAY = "weekday"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"


class Transportation(Base):
    """
    Transportation service model for private transport.

    Attributes:
        id: Unique identifier (UUID)
        vendor_id: Associated vendor ID
        service_type: Type of service (airport, tour, custom)
        vehicle_type: Type of vehicle
        vehicle_description: Description of vehicle
        capacity: Passenger capacity
        features: JSON dict of features (wifi, ac, bluetooth)
        images: JSON list of image URLs
        pricing_type: Pricing model
        base_price: Base price amount
        price_per_km: Price per kilometer
        price_per_hour: Price per hour
        routes_served: JSON list of predefined routes
        locations: JSON list of service areas
        rating: Average rating
        total_reviews: Number of reviews
        total_bookings: Total bookings count
        is_available: Availability status
        is_active: Active status
    """

    __tablename__ = "transportation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )

    service_type = Column(
        Enum(TransportServiceType),
        default=TransportServiceType.AIRPORT_TRANSFER,
        nullable=False,
    )
    vehicle_type = Column(
        Enum(TransportVehicleType), default=TransportVehicleType.SEDAN, nullable=False
    )

    vehicle_description = Column(String(255), nullable=True)
    capacity = Column(Integer, default=4)

    features = Column(JSONB, default=dict)
    images = Column(JSON, default=list)

    pricing_type = Column(
        Enum(PricingType), default=PricingType.PER_ROUTE, nullable=False
    )
    base_price = Column(Numeric(10, 2), default=0)
    price_per_km = Column(Numeric(10, 2), default=0)
    price_per_hour = Column(Numeric(10, 2), default=0)

    routes_served = Column(JSON, default=list)
    locations = Column(JSON, default=list)

    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    total_bookings = Column(Integer, default=0)

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
    vendor = relationship("Vendor", back_populates="transportation")

    # Indexes for performance
    __table_args__ = (
        Index("idx_transport_vendor", "vendor_id"),
        Index("idx_transport_is_active", "is_active"),
        Index("idx_transport_is_available", "is_available"),
        Index("idx_transport_created_at", "created_at"),
        Index("idx_transport_service_type", "service_type"),
        Index("idx_transport_vehicle_type", "vehicle_type"),
        Index("idx_transport_available", "is_available", "is_active", "deleted_at"),
        Index("idx_transport_price", "base_price"),
        Index("idx_transport_deleted", "deleted_at"),
        # GIN index for features JSON search
        Index("idx_transport_features_gin", "features", postgresql_using="gin"),
        sa.CheckConstraint("capacity > 0", name="chk_transport_capacity"),
        sa.CheckConstraint("base_price >= 0", name="chk_transport_price"),
    )
