import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class TripPlan(Base):
    __tablename__ = "trip_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    travelers = Column(Integer, nullable=False, default=1)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    total_estimated = Column(Float, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    is_shared = Column(Boolean, nullable=False, default=False)
    is_template = Column(Boolean, nullable=False, default=False)
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

    __table_args__ = (Index("ix_trip_plans_user_status", "user_id", "status"),)


class TripItem(Base):
    __tablename__ = "trip_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trip_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_index = Column(Integer, nullable=False, default=0)
    item_type = Column(String(30), nullable=False)
    reference_type = Column(String(30), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=False)
    label = Column(String(300), nullable=True)
    location = Column(String(200), nullable=True)
    start_time = Column(Time(timezone=True), nullable=True)
    end_time = Column(Time(timezone=True), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0)
    total_price = Column(Float, nullable=False, default=0)
    commission_rate = Column(Float, nullable=True)
    commission_amount = Column(Float, nullable=False, default=0)
    vendor_payout = Column(Float, nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(20), nullable=False, default="tentative")
    sort_order = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)
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

    __table_args__ = (Index("ix_trip_items_plan_day", "plan_id", "day_index"),)
