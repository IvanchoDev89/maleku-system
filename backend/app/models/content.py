import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class StaticPage(Base):
    __tablename__ = "static_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False, default="")
    template = Column(String(100), nullable=True)
    meta_title = Column(String(70), nullable=True)
    meta_description = Column(String(160), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    show_in_footer = Column(Boolean, default=False, nullable=False)
    show_in_header = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

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
        Index("idx_static_pages_active", "is_active"),
        Index("idx_static_pages_slug", "slug"),
        Index("idx_static_pages_sort", "sort_order"),
    )


class SEOSettings(Base):
    __tablename__ = "seo_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_title_template = Column(String(200), default="{page_title} | {site_name}", nullable=False)
    default_meta_title = Column(String(200), default="Costa Rica Travel - Tours, Hotels & Vacation Packages", nullable=False)
    default_meta_description = Column(Text, default="Discover the best of Costa Rica with our curated tours, hotels, and vacation packages.", nullable=False)
    default_meta_keywords = Column(JSONB, default=list, nullable=False)
    google_site_verification = Column(String(255), nullable=True)
    robots_txt = Column(Text, default="User-agent: *\nDisallow: /admin/\nDisallow: /superadmin/", nullable=False)
    sitemap_enabled = Column(Boolean, default=True, nullable=False)
    structured_data_enabled = Column(Boolean, default=True, nullable=False)

    updated_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

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

    updater = relationship("User", lazy="selectin")


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(500), unique=True, nullable=False)
    original_name = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    url = Column(String(1000), nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    alt_text = Column(String(500), nullable=True)
    folder = Column(String(100), nullable=True)

    uploaded_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    used_in = Column(JSONB, default=list, nullable=False)

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

    uploader = relationship("User", lazy="selectin")

    __table_args__ = (
        Index("idx_media_files_folder", "folder"),
        Index("idx_media_files_mime", "mime_type"),
        Index("idx_media_files_uploaded_by", "uploaded_by"),
    )
