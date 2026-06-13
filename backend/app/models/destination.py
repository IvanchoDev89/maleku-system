"""
Destination model for travel locations and regions.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, JSON, Index
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class Destination(Base):
    """
    Destination model representing Costa Rican regions and locations.

    Attributes:
        id: Unique identifier (UUID)
        name: Destination name
        slug: URL-friendly identifier
        description: Full description
        region: Region/state
        province: Province
        highlights: JSON list of highlights
        things_to_do: JSON list of activities
        best_time: Best time to visit description
        image: Main image URL
        gallery: JSON list of gallery images
        order: Display order
        is_active: Active status
        is_featured: Featured destination flag
    """

    __tablename__ = "destinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    # Location
    region = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)

    # Content
    highlights = Column(JSON, default=list)
    things_to_do = Column(JSON, default=list)
    best_time = Column(Text, nullable=True)

    # Media
    image = Column(String(500), nullable=True)
    gallery = Column(JSON, default=list)

    # Display
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False)

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
        Index("idx_destination_region", "region"),
        Index("idx_destination_order", "order"),
        Index("idx_destination_featured", "is_featured", "is_active"),
    )
