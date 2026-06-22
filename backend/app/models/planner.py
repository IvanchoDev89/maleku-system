import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class PlannerLead(Base):
    __tablename__ = "planner_leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    duration = Column(String(10), nullable=False)
    budget = Column(Integer, nullable=False)
    style = Column(String(20), nullable=False)
    destinations = Column(JSON, nullable=False, default=list)
    travelers = Column(Integer, nullable=False, default=2)
    season = Column(String(20), default="any")
    transport = Column(String(20), default="shuttle")
    accommodation = Column(String(20), default="mid")
    notes = Column(Text, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    total_days = Column(Integer, nullable=True)
    itinerary = Column(JSON, nullable=True)

    # Lead status
    status = Column(String(20), default="new")
    contacted_at = Column(DateTime(timezone=True), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    notes_admin = Column(Text, nullable=True)

    # IP tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

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
