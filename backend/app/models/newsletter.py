"""
Newsletter subscriber model for email marketing.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class NewsletterSubscriber(Base):
    """
    Newsletter subscriber model for email list management.
    
    Attributes:
        id: Unique identifier (UUID)
        email: Subscriber email address
        first_name: Optional first name
        is_active: Whether subscription is active
        is_confirmed: Whether email is confirmed
        source: Where the subscription came from (e.g., 'landing_page', 'footer')
        confirmation_token: Token for email confirmation
        unsubscribed_at: When the user unsubscribed
        created_at: Subscription timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "newsletter_subscribers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    
    # Subscription status
    is_active = Column(Boolean, default=True, nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    source = Column(String(50), default="landing_page")
    confirmation_token = Column(String(100), nullable=True)
    
    # Tracking
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    __table_args__ = (
        Index('idx_newsletter_active', 'is_active', 'is_confirmed'),
        Index('idx_newsletter_created', 'created_at'),
    )
