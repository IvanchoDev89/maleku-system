"""
Flight model for flight booking marketplace.
"""

import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Enum,
    Index,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class RouteType(str, enum.Enum):
    """Flight route type enumeration."""

    INTERNATIONAL = "international"
    DOMESTIC = "domestic"


class Flight(Base):
    """
    Flight model for airline bookings.

    Attributes:
        id: Unique identifier (UUID)
        vendor_id: Associated vendor ID (optional)
        airline: Airline name
        flight_number: Flight number
        route_type: International or domestic
        origin_airport: Origin IATA code
        destination_airport: Destination IATA code
        departure_time: Departure time (HH:MM)
        arrival_time: Arrival time (HH:MM)
        duration_minutes: Flight duration
        aircraft_type: Aircraft model
        price_economy: Economy class price
        price_business: Business class price
        price_first: First class price
        currency: Currency code
        baggage_allowance: JSON dict of baggage allowances
        amenities: JSON list of amenities (wifi, meals, etc.)
        schedule_days: JSON list of operating days
        is_active: Active status
    """

    __tablename__ = "flights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=True
    )

    airline = Column(String(100), nullable=False)
    flight_number = Column(String(20), nullable=False)

    route_type = Column(Enum(RouteType), default=RouteType.DOMESTIC, nullable=False)
    origin_airport = Column(String(10), nullable=False)
    destination_airport = Column(String(10), nullable=False)

    departure_time = Column(String(10), nullable=False)
    arrival_time = Column(String(10), nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    aircraft_type = Column(String(100), nullable=True)

    price_economy = Column(Numeric(10, 2), default=0)
    price_business = Column(Numeric(10, 2), default=0)
    price_first = Column(Numeric(10, 2), default=0)

    currency = Column(String(3), default="USD")

    baggage_allowance = Column(JSON, default=dict)
    amenities = Column(JSON, default=list)
    schedule_days = Column(JSON, default=list)

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
    vendor = relationship("Vendor", back_populates="flights")

    # Indexes for performance
    __table_args__ = (
        Index("idx_flight_vendor", "vendor_id"),
        Index("idx_flight_destination", "destination_airport"),
        Index("idx_flight_departure", "departure_time"),
        Index("idx_flight_active_departure", "is_active", "departure_time"),
        Index("idx_flight_route", "origin_airport", "destination_airport"),
        Index("idx_flight_route_type", "route_type"),
        Index("idx_flight_active", "is_active", "deleted_at"),
        Index("idx_flight_price", "price_economy"),
        Index("idx_flight_deleted", "deleted_at"),
    )
