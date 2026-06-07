"""
Tour model for adventure and experience listings.
"""
import uuid
import enum
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Float, Integer, JSON, Enum, Index, Numeric, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class TourCategory(enum.Enum):
    """Tour category enumeration."""
    ADVENTURE = "adventure"
    NATURE = "nature"
    CULTURAL = "cultural"
    WATER = "water"
    WELLNESS = "wellness"
    GASTRONOMY = "gastronomy"


class TourDifficulty(enum.Enum):
    """Tour difficulty level enumeration."""
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"


class Tour(Base):
    """
    Tour model representing experiences and activities.
    
    Attributes:
        id: Unique identifier (UUID)
        vendor_id: Associated vendor ID
        name: Tour name
        slug: URL-friendly identifier
        description: Full description
        category: Tour category
        difficulty: Difficulty level
        duration_hours: Duration in hours
        duration_text: Human-readable duration
        location: Location/region
        meeting_point: Meeting point address
        included: JSON list of what's included
        not_included: JSON list of exclusions
        itinerary: JSON list of stops/activities
        max_group_size: Maximum participants
        min_age: Minimum age requirement
        price: Base price per person
        currency: Currency code (USD)
        images: JSON list of image URLs
        cover_image: Main cover image URL
        schedule_days: Available days of week
        rating: Average rating
        total_reviews: Number of reviews
        total_bookings: Number of bookings
        is_featured: Featured listing flag
        is_active: Active status
    """
    __tablename__ = "tours"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(TourCategory), nullable=False)
    difficulty = Column(Enum(TourDifficulty), default=TourDifficulty.EASY)
    
    duration_hours = Column(Float, nullable=False)
    duration_text = Column(String(50), nullable=True)
    
    location = Column(String(255), nullable=True)
    meeting_point = Column(String(500), nullable=True)
    
    included = Column(JSONB, default=list)
    not_included = Column(JSONB, default=list)
    itinerary = Column(JSONB, default=list)
    
    max_group_size = Column(Integer, default=15)
    min_age = Column(Integer, default=0)
    
    price = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")
    
    images = Column(JSON, default=list)
    cover_image = Column(String(500), nullable=True)
    
    schedule_days = Column(JSON, default=list)
    
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    total_bookings = Column(Integer, default=0)
    
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="tours")
    bookings = relationship("Booking", back_populates="tour", lazy="selectin")
    reviews = relationship("Review", back_populates="tour", lazy="selectin")
    
    __table_args__ = (
        Index('idx_tour_vendor', 'vendor_id'),
        Index('idx_tour_category', 'category'),
        Index('idx_tour_active', 'is_active'),
        Index('idx_tour_featured', 'is_featured', 'is_active', 'deleted_at'),
        Index('idx_tour_price', 'price'),
        Index('idx_tour_deleted', 'deleted_at'),
        # GIN index for included items array search
        Index('idx_tour_included_gin', 'included', postgresql_using='gin'),
        # Full-text search index (Spanish).
        # Using raw text() so SQLAlchemy does not need to compile the
        # expression; this is identical to the migration's
        # CREATE INDEX ... USING gin (to_tsvector(...)) statement and lets
        # ``Base.metadata.create_all`` work in tests.
        Index(
            'idx_tour_fts',
            text("to_tsvector('spanish', COALESCE(name, '') || ' ' || "
                 "COALESCE(description, '') || ' ' || COALESCE(location, ''))"),
            postgresql_using='gin',
        ),
        # CHECK constraints for data integrity
        sa.CheckConstraint('rating >= 0 AND rating <= 5', name='chk_tour_rating'),
        sa.CheckConstraint('price >= 0', name='chk_tour_price_positive'),
        sa.CheckConstraint('duration_hours > 0', name='chk_tour_duration_positive'),
        sa.CheckConstraint('min_age >= 0', name='chk_tour_min_age'),
        sa.CheckConstraint('max_group_size > 0', name='chk_tour_group_size'),
    )
