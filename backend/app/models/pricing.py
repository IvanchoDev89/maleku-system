"""
Pricing Rule model for dynamic pricing.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Float,
    Integer,
    Enum,
    Index,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.models.transportation import DayType


class PricingRule(Base):
    """
    Pricing rule model for dynamic pricing rules.

    Attributes:
        id: Unique identifier (UUID)
        service_type: Type of service (vehicle, boat, flight, transport, property, tour)
        service_id: ID of the specific service
        base_price: Base price amount
        demand_multiplier: Multiplier for demand (0.8 - 3.0)
        seasonal_multiplier: Multiplier for season (0.8 - 1.5)
        date_from: Start date for rule validity
        date_to: End date for rule validity
        day_type: Type of day (weekday, weekend, holiday)
        min_occupancy: Minimum occupancy for rule
        max_occupancy: Maximum occupancy for rule
        advance_booking_days: Days in advance for early bird
        advance_discount_percent: Discount percentage for early booking
        is_active: Whether rule is active
    """

    __tablename__ = "pricing_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    service_type = Column(String(50), nullable=False)
    service_id = Column(UUID(as_uuid=True), nullable=False)

    base_price = Column(Numeric(10, 2), nullable=False)

    demand_multiplier = Column(Float, default=1.0)
    seasonal_multiplier = Column(Float, default=1.0)

    date_from = Column(DateTime(timezone=True), nullable=False)
    date_to = Column(DateTime(timezone=True), nullable=True)

    day_type = Column(Enum(DayType), nullable=True)

    min_occupancy = Column(Integer, nullable=True)
    max_occupancy = Column(Integer, nullable=True)

    advance_booking_days = Column(Integer, nullable=True)
    advance_discount_percent = Column(Float, default=0)

    is_active = Column(Boolean, default=True, nullable=False)

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

    # Indexes for performance
    __table_args__ = (
        Index("idx_pricing_service", "service_type", "service_id"),
        Index("idx_pricing_active", "is_active"),
        Index("idx_pricing_date_range", "date_from", "date_to"),
    )
