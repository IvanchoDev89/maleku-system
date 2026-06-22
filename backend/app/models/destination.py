"""
Destination model for travel locations and regions.
Supports hierarchical geography: Country -> Province -> Canton -> District.
Includes rich travel content, practical info, media, and SEO metadata.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    Integer,
    Float,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)

    # Geographic hierarchy
    country = Column(String(100), default="Costa Rica", nullable=False)
    region = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    canton = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)

    # Coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    zoom = Column(Integer, default=10)

    # Core content
    description = Column(Text, nullable=True)
    highlights = Column(JSON, default=list)
    things_to_do = Column(JSON, default=list)

    # Enriched travel content
    culture = Column(Text, nullable=True)
    gastronomy = Column(Text, nullable=True)
    history = Column(Text, nullable=True)
    best_time = Column(Text, nullable=True)
    weather_info = Column(Text, nullable=True)
    getting_there = Column(Text, nullable=True)
    local_tips = Column(Text, nullable=True)
    safety_info = Column(Text, nullable=True)

    # Practical information
    language = Column(String(100), nullable=True)
    currency = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    phone_code = Column(String(10), nullable=True)
    visa_info = Column(Text, nullable=True)
    emergency_numbers = Column(JSON, default=list)

    # Media
    image = Column(String(500), nullable=True)
    gallery = Column(JSON, default=list)
    videos = Column(JSON, default=list)
    featured_photo = Column(String(500), nullable=True)

    # SEO
    seo_title = Column(String(70), nullable=True)
    seo_description = Column(String(160), nullable=True)
    seo_keywords = Column(JSON, default=list)

    # Display
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False)

    # Soft delete
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

    __table_args__ = (
        Index("idx_destination_is_active", "is_active"),
        Index("idx_destination_is_featured", "is_featured"),
        Index("idx_destination_created_at", "created_at"),
        Index("idx_destination_region", "region"),
        Index("idx_destination_province", "province"),
        Index("idx_destination_canton", "canton"),
        Index("idx_destination_country", "country"),
        Index("idx_destination_order", "order"),
        Index("idx_destination_featured", "is_featured", "is_active"),
    )
