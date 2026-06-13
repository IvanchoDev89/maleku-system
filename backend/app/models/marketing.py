"""
Marketing Campaign Models for BillionMail Integration
Manages email campaigns, templates, and subscriber lists
"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Boolean,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class CampaignStatus(str, PyEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class CampaignType(str, PyEnum):
    NEWSLETTER = "newsletter"
    PROMOTION = "promotion"
    WELCOME = "welcome"
    AUTOMATED = "automated"
    TRANSACTIONAL = "transactional"


class RecipientType(str, PyEnum):
    ALL_USERS = "all_users"
    VENDOR_CUSTOMERS = "vendor_customers"
    SEGMENT = "segment"
    INDIVIDUAL = "individual"


class EmailCampaign(Base):
    """
    Email marketing campaigns for newsletter and promotions
    """

    __tablename__ = "email_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)

    # Campaign metadata
    campaign_type = Column(
        Enum(CampaignType), default=CampaignType.NEWSLETTER, nullable=False
    )
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)

    # Content
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("email_templates.id"), nullable=True
    )
    html_content = Column(JSONB, nullable=True)
    text_content = Column(JSONB, nullable=True)

    # Targeting
    recipient_type = Column(
        Enum(RecipientType), default=RecipientType.ALL_USERS, nullable=False
    )
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)
    recipient_list = Column(
        JSONB, nullable=True
    )  # For INDIVIDUAL type: [user_id, user_id, ...]
    segment_criteria = Column(
        JSONB, nullable=True
    )  # For SEGMENT type: {"min_bookings": 5, "location": "..."}

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Sender
    from_name = Column(String(100), nullable=False, default="Costa Rica Travel")
    from_email = Column(
        String(255), nullable=False, default="noreply@costaricatravel.dev"
    )
    reply_to = Column(String(255), nullable=True)

    # Statistics
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    bounced_count = Column(Integer, default=0)
    unsubscribed_count = Column(Integer, default=0)

    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)

    # A/B Testing
    ab_test_enabled = Column(Boolean, default=False)
    ab_test_variants = Column(JSON, nullable=True)  # Store variant content
    ab_test_winner = Column(String(50), nullable=True)

    # Creator
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

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
    template = relationship("EmailTemplate", back_populates="campaigns")
    creator = relationship("User", foreign_keys=[created_by])
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    logs = relationship(
        "EmailLog", back_populates="campaign", cascade="all, delete-orphan"
    )

    __table_args__ = (
        # Index for querying by status and scheduled time
        Index("idx_campaign_status_scheduled", "status", "scheduled_at"),
        Index("idx_campaign_vendor_created", "vendor_id", "created_at"),
        Index("idx_campaign_type_status", "campaign_type", "status"),
    )


class EmailTemplate(Base):
    """
    Reusable email templates
    """

    __tablename__ = "email_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Template type
    template_type = Column(
        Enum(CampaignType), default=CampaignType.NEWSLETTER, nullable=False
    )
    is_system = Column(Boolean, default=False)  # System templates can't be deleted

    # Content
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    preview_image = Column(String(500), nullable=True)

    # Variables that can be used in template
    available_variables = Column(JSONB, nullable=True)

    # Creator (null for system templates)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True)

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
    campaigns = relationship("EmailCampaign", back_populates="template")
    creator = relationship("User", foreign_keys=[created_by])
    vendor = relationship("Vendor", foreign_keys=[vendor_id])


class EmailLog(Base):
    """
    Individual email sending logs
    """

    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # References
    campaign_id = Column(
        UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=True
    )
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Recipient info (snapshot at send time)
    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(255), nullable=True)

    # Email details
    subject = Column(String(255), nullable=False)
    message_id = Column(
        String(255), nullable=True
    )  # External message ID from BillionMail

    # Status tracking
    status = Column(
        String(50), default="queued", nullable=False
    )  # queued, sent, delivered, opened, clicked, bounced, failed

    # Engagement tracking
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)

    # Links clicked
    clicked_links = Column(JSONB, nullable=True)

    # Error info
    error_message = Column(Text, nullable=True)
    bounce_reason = Column(String(255), nullable=True)

    # User agent and IP when opened/clicked
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    campaign = relationship("EmailCampaign", back_populates="logs")
    recipient = relationship("User", foreign_keys=[recipient_id])

    __table_args__ = (
        Index("idx_log_campaign_status", "campaign_id", "status"),
        Index("idx_log_recipient_created", "recipient_email", "created_at"),
        Index("idx_log_message_id", "message_id"),
    )


class MarketingAutomation(Base):
    """
    Automated email workflows
    """

    __tablename__ = "marketing_automations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Trigger configuration
    trigger_type = Column(
        String(50), nullable=False
    )  # user_signup, booking_created, booking_completed, abandoned_cart, etc.
    trigger_criteria = Column(JSONB, nullable=True)  # Additional filter conditions

    # Automation steps (sequence of emails)
    steps = Column(
        JSONB, nullable=False
    )  # [{"delay_hours": 0, "template_id": "...", "subject": "..."}, ...]

    # Status
    is_active = Column(Boolean, default=True)

    # Targeting
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True
    )  # null = global automation

    # Statistics
    total_triggered = Column(Integer, default=0)
    total_completed = Column(Integer, default=0)

    # Creator
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

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
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    creator = relationship("User", foreign_keys=[created_by])


class InboxMessage(Base):
    """
    Unified inbox for customer-vendor communications
    """

    __tablename__ = "inbox_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Participants
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=True
    )  # null = message to platform admin

    # Thread grouping
    thread_id = Column(UUID(as_uuid=True), nullable=False)  # Groups related messages

    # Message content
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # Message type
    message_type = Column(
        String(50), default="inquiry", nullable=False
    )  # inquiry, support, booking_question, review_reply, etc.

    # Related entities
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True)
    tour_id = Column(UUID(as_uuid=True), ForeignKey("tours.id"), nullable=True)

    # Status
    is_from_customer = Column(
        Boolean, default=True
    )  # True = customer sent, False = vendor/admin replied
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Priority and escalation
    priority = Column(
        String(20), default="normal", nullable=False
    )  # low, normal, high, urgent
    is_escalated = Column(Boolean, default=False)
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    customer = relationship(
        "User", foreign_keys=[customer_id], back_populates="inbox_messages"
    )
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    escalated_to_user = relationship("User", foreign_keys=[escalated_to])


class EmailPreference(Base):
    """
    User email subscription preferences
    """

    __tablename__ = "email_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )

    # Global preferences
    marketing_emails = Column(Boolean, default=True)
    booking_notifications = Column(Boolean, default=True)
    promotional_emails = Column(Boolean, default=True)
    newsletter = Column(Boolean, default=True)

    # Vendor-specific preferences (JSONB: {vendor_id: true/false})
    vendor_preferences = Column(JSONB, default=dict)

    # Category preferences
    categories = Column(
        JSONB, default=dict
    )  # { "deals": true, "new_properties": false, ...}

    # Frequency
    email_frequency = Column(
        String(20), default="daily", nullable=False
    )  # immediate, daily, weekly, never

    # Unsubscribe all
    unsubscribed_all = Column(Boolean, default=False)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)

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
    user = relationship("User", back_populates="email_preferences")
