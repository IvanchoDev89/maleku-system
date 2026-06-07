"""
Chat/Conversation Schemas
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models import ChatServiceType, MessageType


class ConversationBase(BaseModel):
    service_type: ChatServiceType = ChatServiceType.GENERAL
    service_id: Optional[UUID] = None


class ConversationCreate(ConversationBase):
    participant_vendor_id: Optional[UUID] = None


class ConversationUpdate(BaseModel):
    is_active: Optional[bool] = None


class ConversationResponse(ConversationBase):
    id: UUID
    participant_user_id: Optional[UUID]
    participant_vendor_id: Optional[UUID]
    last_message_at: Optional[datetime]
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(ConversationResponse):
    last_message: Optional[dict] = None
    unread_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class MessageBase(BaseModel):
    message_type: MessageType = MessageType.TEXT
    content: str = Field(..., min_length=1)
    attachments: List[dict] = []


class MessageCreate(MessageBase):
    pass


class MessageUpdate(BaseModel):
    read_at: Optional[datetime] = None


class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    sender_type: str
    read_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageDetailResponse(MessageResponse):
    pass