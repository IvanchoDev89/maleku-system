"""
Booking model for property and tour reservations.
"""

import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,
    Integer,
    Enum,
    Index,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BookingStatus


class Booking(Base):
    """
    Booking model representing property and tour reservations.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Customer user ID
        vendor_id: Vendor providing the service
        property_id: Property for accommodation bookings
        room_id: Specific room for accommodation
        tour_id: Tour for experience bookings
        booking_type: 'property' or 'tour'
        status: Booking lifecycle status
        check_in: Check-in date/time (for properties)
        check_out: Check-out date/time (for properties)
        guests: Number of guests (for properties)
        participants: Number of participants (for tours)
        guest_name: Lead guest name
        guest_email: Lead guest email
        guest_phone: Lead guest phone
        guest_notes: Special requests or notes
        subtotal: Base amount before commission
        commission_amount: Platform commission
        total_amount: Final charge amount
        currency: Currency code
        stripe_payment_intent_id: Stripe payment ID
        stripe_payment_status: Stripe payment status
        confirmation_code: Unique booking reference
    """

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relations
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True
    )
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="SET NULL"),
        nullable=True,
    )
    room_id = Column(
        UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True
    )
    tour_id = Column(
        UUID(as_uuid=True), ForeignKey("tours.id", ondelete="SET NULL"), nullable=True
    )

    # Booking Details
    booking_type = Column(String(20), nullable=False)  # property or tour
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    # Dates (for properties)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)

    # People
    guests = Column(Integer, default=1)
    participants = Column(Integer, default=1)

    # Guest Info
    guest_name = Column(String(255), nullable=False)
    guest_email = Column(String(255), nullable=False)
    guest_phone = Column(String(20), nullable=True)
    guest_notes = Column(Text, nullable=True)

    # Pricing
    subtotal = Column(Numeric(10, 2), default=0)
    commission_amount = Column(Numeric(10, 2), default=0)
    total_amount = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")

    # Payment
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_payment_status = Column(String(50), nullable=True)

    # Reference
    confirmation_code = Column(String(20), unique=True, index=True, nullable=True)

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
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="bookings")
    vendor = relationship("Vendor", back_populates="bookings")
    property = relationship("Property", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    tour = relationship("Tour", back_populates="bookings")
    review = relationship("Review", back_populates="booking", uselist=False)

    __table_args__ = (
        Index("idx_booking_user", "user_id"),
        Index("idx_booking_vendor", "vendor_id"),
        Index("idx_booking_property", "property_id"),
        Index("idx_booking_tour", "tour_id"),
        Index("idx_booking_status", "status", "deleted_at"),
        Index("idx_booking_date", "created_at"),
        Index("idx_booking_checkin", "check_in"),
        Index("idx_booking_deleted", "deleted_at"),
        # Composite index for availability queries
        Index(
            "idx_booking_availability",
            "property_id",
            "room_id",
            "check_in",
            "check_out",
            postgresql_where=sa.text("deleted_at IS NULL"),
        ),
        sa.CheckConstraint("guests > 0", name="chk_booking_guests"),
        sa.CheckConstraint("total_amount >= 0", name="chk_booking_amount_positive"),
    )


class ProcessedWebhook(Base):
    """Track processed webhooks to prevent replay attacks."""

    __tablename__ = "processed_webhooks"
    event_id = Column(String(255), primary_key=True)
    event_type = Column(String(100), nullable=False)
    processed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
