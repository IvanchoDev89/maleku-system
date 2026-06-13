"""
Review model for property and tour ratings.
"""

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
    Integer,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Review(Base):
    """
    Review model for property and tour ratings.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Reviewer user ID
        property_id: Property being reviewed (optional)
        tour_id: Tour being reviewed (optional)
        booking_id: Associated booking
        rating: Rating score (1-5)
        title: Review title
        comment: Review text
        is_approved: Whether review is approved/published
    """

    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Relations
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=True,
    )
    tour_id = Column(
        UUID(as_uuid=True), ForeignKey("tours.id", ondelete="CASCADE"), nullable=True
    )
    booking_id = Column(
        UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True
    )

    # Content
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)

    # Moderation
    is_approved = Column(Boolean, default=True, nullable=False)

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
    user = relationship("User", back_populates="reviews")
    property = relationship("Property", back_populates="reviews")
    tour = relationship("Tour", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")

    __table_args__ = (
        Index("idx_review_property", "property_id"),
        Index("idx_review_tour", "tour_id"),
        Index("idx_review_user", "user_id"),
        Index("idx_review_booking", "booking_id"),
        Index("idx_review_approved", "is_approved", "deleted_at"),
        Index("idx_review_deleted", "deleted_at"),
        sa.CheckConstraint(
            "rating >= 1 AND rating <= 5", name="chk_review_rating_range"
        ),
    )
