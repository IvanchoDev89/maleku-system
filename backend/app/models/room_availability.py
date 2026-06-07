"""
Room Availability model for calendar-based availability management.
Efficiently tracks room availability by date with support for dynamic pricing.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Date, DateTime, ForeignKey, Float, Boolean, Index, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class RoomAvailability(Base):
    """
    Calendar of room availability by date.
    Optimized for querying availability ranges and dynamic pricing.
    
    Attributes:
        id: Unique identifier (UUID)
        room_id: Associated room ID
        date: Specific date for this availability record
        is_available: Whether room is available on this date
        price_override: Special price for this date (NULL = use room default)
        min_stay: Minimum nights required (NULL = no minimum)
        max_stay: Maximum nights allowed (NULL = no maximum)
        close_to_arrival: Cannot check in on this date
        close_to_departure: Cannot check out on this date
        notes: Internal notes (e.g., "maintenance", "special event")
    """
    __tablename__ = "room_availability"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relations
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    
    # Date
    date = Column(Date, nullable=False)
    
    # Availability status
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Dynamic pricing
    price_override = Column(Numeric(10, 2), nullable=True)  # NULL = use room.price_per_night
    
    # Stay constraints
    min_stay = Column(Float, nullable=True)  # Minimum consecutive nights
    max_stay = Column(Float, nullable=True)   # Maximum consecutive nights
    
    # Arrival/departure restrictions
    close_to_arrival = Column(Boolean, default=False)    # Cannot check in
    close_to_departure = Column(Boolean, default=False)  # Cannot check out
    
    # Metadata
    notes = Column(Text, nullable=True)  # Internal notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    room = relationship("Room", back_populates="availability")
    
    # Indexes for efficient queries
    __table_args__ = (
        # Unique constraint: one record per room per date
        Index('idx_room_availability_unique', 'room_id', 'date', unique=True),
        # Query availability for date range
        Index('idx_room_availability_date_range', 'room_id', 'date', 'is_available'),
        # Query by availability status
        Index('idx_room_availability_status', 'is_available', 'date'),
        # Query available rooms for a date
        Index('idx_room_availability_date_lookup', 'date', 'is_available', 'room_id'),
    )
