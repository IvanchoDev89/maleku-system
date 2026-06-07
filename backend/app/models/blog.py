"""
Blog post model for content management.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, JSON, Enum, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BlogPostStatus


class BlogPost(Base):
    """
    Blog post model for travel guides and articles.
    
    Attributes:
        id: Unique identifier (UUID)
        title: Post title
        slug: URL-friendly identifier
        excerpt: Short summary
        content: Full HTML/Markdown content
        featured_image: Cover image URL
        category: Post category
        tags: JSON list of tags
        author_id: Author user ID
        status: Publication status
        published_at: Publication timestamp
        views_count: View counter
        is_featured: Featured post flag
        seo_title: SEO title
        seo_description: SEO meta description
    """
    __tablename__ = "blog_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    
    # Media
    featured_image = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    
    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Publication
    status = Column(Enum(BlogPostStatus), default=BlogPostStatus.DRAFT, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Stats
    views_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    # SEO
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(String(500), nullable=True)
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="blog_posts")
    
    __table_args__ = (
        Index('idx_blog_status', 'status', 'deleted_at'),
        Index('idx_blog_author', 'author_id'),
        Index('idx_blog_category', 'category'),
        Index('idx_blog_featured', 'is_featured', 'status', 'deleted_at'),
        Index('idx_blog_published', 'published_at'),
        Index('idx_blog_deleted', 'deleted_at'),
        # Full-text search index (Spanish).
        # See app/models/tour.py for the rationale behind using raw text().
        Index(
            'idx_blog_fts',
            text("to_tsvector('spanish', COALESCE(title, '') || ' ' || "
                 "COALESCE(content, '') || ' ' || COALESCE(excerpt, ''))"),
            postgresql_using='gin',
        ),
    )
