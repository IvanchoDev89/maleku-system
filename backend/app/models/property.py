"""
Property and Room models for accommodation listings.
"""

import enum
import uuid
from datetime import datetime, timezone
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Float,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class PropertyType(str, enum.Enum):
    """Property accommodation type."""

    HOTEL = "hotel"
    HOSTEL = "hostel"
    ECO_LODGE = "eco_lodge"
    RESORT = "resort"
    VILLA = "villa"
    APARTMENT = "apartment"
    CABIN = "cabin"
    GLAMPING = "glamping"
    BOUTIQUE = "boutique"
    APARTHOTEL = "aparthotel"


class PropertyCategory(str, enum.Enum):
    """Property location category."""

    BEACH = "beach"
    MOUNTAIN = "mountain"
    JUNGLE = "jungle"
    CITY = "city"
    RURAL = "rural"
    LAKE = "lake"


class Property(Base):
    """
    Property model representing accommodation listings.

    Attributes:
        id: Unique identifier (UUID)
        vendor_id: Associated vendor ID
        name: Property name
        slug: URL-friendly identifier
        short_description: Brief description
        description: Full description
        property_type: Type of accommodation
        category: Location category
        location fields: country, province, region, city, district, address
        coordinates: latitude, longitude
        media: images, videos, virtual_tour_url
        amenities: JSON list of amenities
        features: JSON list of features
        policies: check-in/out times, cancellation, house_rules
        capacity: min/max guests, beds, baths, square_meters
        pricing: base_price, currency, weekend_price, weekly_discount
        seo: seo_title, seo_description, seo_keywords
        status: is_active, is_featured, is_verified, rating, total_reviews
    """

    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    short_description = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    property_type = Column(String(20), default=PropertyType.HOTEL.value, nullable=False)
    category = Column(String(20), nullable=True)

    # Location
    country = Column(String(100), default="Costa Rica", nullable=False)
    province = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    map_address = Column(String(500), nullable=True)

    # Media
    cover_image = Column(String(500), nullable=True)
    images = Column(JSON, default=list)
    videos = Column(JSON, default=list)
    virtual_tour_url = Column(String(500), nullable=True)

    # Property Details
    amenities = Column(JSONB, default=list)
    features = Column(JSONB, default=list)

    # Policies
    check_in_time = Column(String(10), default="15:00")
    check_out_time = Column(String(10), default="11:00")
    cancellation_policy = Column(Text, nullable=True)
    house_rules = Column(Text, nullable=True)
    important_info = Column(Text, nullable=True)

    # Capacity
    min_guests = Column(Integer, default=1)
    max_guests = Column(Integer, default=10)
    beds = Column(Integer, default=1)
    baths = Column(Integer, default=1)
    square_meters = Column(Integer, nullable=True)

    # Pricing
    base_price = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")
    weekend_price = Column(Numeric(10, 2), default=0)
    weekly_discount = Column(Numeric(5, 2), default=0)

    # SEO
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(JSONB, default=list)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)

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
    vendor = relationship("Vendor", back_populates="properties")
    rooms = relationship(
        "Room", back_populates="property", cascade="all, delete-orphan", lazy="selectin"
    )
    reviews = relationship("Review", back_populates="property")
    bookings = relationship("Booking", back_populates="property")

    # Indexes
    __table_args__ = (
        Index("idx_property_vendor", "vendor_id"),
        Index("idx_property_is_active", "is_active"),
        Index("idx_property_is_featured", "is_featured"),
        Index("idx_property_created_at", "created_at"),
        Index("idx_property_active_created", "is_active", "created_at"),
        Index("idx_property_vendor_active", "vendor_id", "is_active"),
        Index("idx_property_type", "property_type"),
        Index("idx_property_category", "category"),
        Index("idx_property_location", "region", "city"),
        Index("idx_property_featured", "is_featured", "is_active", "deleted_at"),
        Index("idx_property_price", "base_price"),
        Index("idx_property_geo", "latitude", "longitude"),
        Index("idx_property_deleted", "deleted_at"),
        # GIN index for amenities array search
        Index("idx_property_amenities_gin", "amenities", postgresql_using="gin"),
        # GIN index for features JSON search
        Index("idx_property_features_gin", "features", postgresql_using="gin"),
        # Full-text search index (Spanish).
        # See app/models/tour.py for the rationale behind using raw text().
        Index(
            "idx_property_fts",
            sa.text(
                "to_tsvector('spanish', COALESCE(name, '') || ' ' || "
                "COALESCE(short_description, '') || ' ' || "
                "COALESCE(description, '') || ' ' || "
                "COALESCE(city, '') || ' ' || COALESCE(region, ''))"
            ),
            postgresql_using="gin",
        ),
        # CHECK constraints for data integrity
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="chk_property_rating"),
        sa.CheckConstraint("min_guests > 0", name="chk_property_min_guests"),
        sa.CheckConstraint("max_guests >= min_guests", name="chk_property_capacity"),
        sa.CheckConstraint("base_price >= 0", name="chk_property_base_price"),
        sa.CheckConstraint(
            "latitude IS NULL OR (latitude >= -90 AND latitude <= 90)",
            name="chk_property_latitude",
        ),
        sa.CheckConstraint(
            "longitude IS NULL OR (longitude >= -180 AND longitude <= 180)",
            name="chk_property_longitude",
        ),
    )


class Room(Base):
    """
    Room model representing individual rooms/units within a property.

    Attributes:
        id: Unique identifier (UUID)
        property_id: Associated property ID
        name: Room name/type
        description: Room description
        capacity: max_guests, beds
        pricing: price_per_night, extra_guest_price, cleaning_fee
        availability: is_available
    """

    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(
        UUID(as_uuid=True),
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Capacity
    max_guests = Column(Integer, default=2)
    beds = Column(Integer, default=1)
    bed_type = Column(String(100), nullable=True)

    # Pricing
    price_per_night = Column(Numeric(10, 2), default=0)
    weekend_price = Column(Numeric(10, 2), default=0)
    extra_guest_price = Column(Numeric(10, 2), default=0)
    cleaning_fee = Column(Numeric(10, 2), default=0)

    # Media
    images = Column(JSON, default=list)

    # Status
    is_available = Column(Boolean, default=True)

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
    property = relationship("Property", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room", lazy="selectin")
    availability = relationship(
        "RoomAvailability",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
