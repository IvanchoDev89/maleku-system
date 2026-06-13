"""
Chat models for user-vendor messaging.
"""

import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Enum,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class ChatServiceType(enum.Enum):
    """Type of service related to the conversation."""

    GENERAL = "general"
    PROPERTY = "property"
    TOUR = "tour"
    VEHICLE = "vehicle"
    BOAT = "boat"
    FLIGHT = "flight"
    TRANSPORTATION = "transportation"


class MessageType(enum.Enum):
    """Type of message content."""

    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"
    BOOKING_REQUEST = "booking_request"


class Conversation(Base):
    """
    Conversation model representing a chat thread.

    Attributes:
        id: Unique identifier (UUID)
        participant_user_id: User participant ID
        participant_vendor_id: Vendor participant ID
        service_type: Related service type
        service_id: Related service ID (property, tour, etc.)
        last_message_at: Timestamp of last message
        is_active: Whether conversation is active
    """

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    participant_user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    participant_vendor_id = Column(
        UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=True
    )

    service_type = Column(
        Enum(ChatServiceType), default=ChatServiceType.GENERAL, nullable=False
    )
    service_id = Column(UUID(as_uuid=True), nullable=True)

    last_message_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    participant_user = relationship(
        "User", foreign_keys=[participant_user_id], back_populates="conversations"
    )
    participant_vendor = relationship(
        "Vendor", foreign_keys=[participant_vendor_id], back_populates="conversations"
    )
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_conv_participant", "participant_user_id", "participant_vendor_id"),
        Index("idx_conv_service", "service_type", "service_id"),
        Index("idx_conv_active", "is_active", "last_message_at", "deleted_at"),
        Index("idx_conv_deleted", "deleted_at"),
    )


class Message(Base):
    """
    Message model representing individual chat messages.

    Attributes:
        id: Unique identifier (UUID)
        conversation_id: Parent conversation ID
        sender_id: Sender user/vendor ID
        sender_type: Type of sender (user, vendor, system)
        message_type: Content type
        content: Message text/content
        attachments: JSON list of file/image URLs
        read_at: When message was read
    """

    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    sender_id = Column(UUID(as_uuid=True), nullable=False)
    sender_type = Column(String(20), nullable=False)  # user, vendor, system

    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=False)

    attachments = Column(JSON, default=list)

    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_message_conversation", "conversation_id"),
        Index("idx_message_sender", "sender_id"),
        Index("idx_message_created", "created_at"),
        Index("idx_message_read", "read_at"),
        Index("idx_message_deleted", "deleted_at"),
    )
