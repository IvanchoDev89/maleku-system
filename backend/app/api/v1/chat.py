"""
Chat/Conversation API - WebSocket Ready
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, UserRole, Vendor, Conversation, Message, ChatServiceType
from app.schemas import chat as chat_schema
from pydantic import BaseModel

router = APIRouter()


class DeleteResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str


class MarkReadResponse(BaseModel):
    message: str
    conversation_id: str


class ReorderResponse(BaseModel):
    message: str
    items_updated: int


class ActivateResponse(BaseModel):
    message: str
    is_active: bool


class ChangeRoleResponse(BaseModel):
    message: str
    user_id: str
    new_role: str


class VerifyResponse(BaseModel):
    message: str
    is_verified: bool


class ToggleActiveResponse(BaseModel):
    message: str
    is_active: bool


class PresignedUrlResponse(BaseModel):
    url: str
    expires_in: int
    fields: dict


async def get_participant_vendor(db: AsyncSession, current_user: User) -> Vendor | None:
    """Fetch the vendor profile associated with the current user (if any)."""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    return result.scalar_one_or_none()


def assert_conversation_participant(
    conversation: Conversation,
    current_user: User,
    vendor: Vendor | None,
) -> None:
    """SECURITY: enforce that the current user is a participant of the conversation.

    Prevents BOLA (OWASP API1:2023). Raises 403 otherwise.
    Admins/super_admins can read all conversations.
    """
    if current_user.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        return
    is_user = conversation.participant_user_id == current_user.id
    is_vendor = vendor is not None and conversation.participant_vendor_id == vendor.id
    if not (is_user or is_vendor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant of this conversation",
        )


@router.get("", response_model=list[chat_schema.ConversationDetailResponse])
async def list_conversations(
    service_type: ChatServiceType = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's conversations"""
    vendor = await get_participant_vendor(db, current_user)

    if current_user.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        query = select(Conversation).where(Conversation.is_active)
    elif vendor:
        query = select(Conversation).where(
            Conversation.is_active,
            (Conversation.participant_user_id == current_user.id)
            | (Conversation.participant_vendor_id == vendor.id),
        )
    else:
        query = select(Conversation).where(
            Conversation.is_active, Conversation.participant_user_id == current_user.id
        )

    if service_type:
        query = query.where(Conversation.service_type == service_type)

    # Apply eager loading to avoid N+1 queries
    query = query.options(
        selectinload(Conversation.participant_user),
        selectinload(Conversation.participant_vendor),
    )

    result = await db.execute(query.order_by(desc(Conversation.last_message_at)))
    conversations = result.scalars().all()

    return conversations


@router.post("", response_model=chat_schema.ConversationResponse)
async def create_conversation(
    conv_data: chat_schema.ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or get existing conversation"""
    if conv_data.participant_vendor_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.participant_user_id == current_user.id,
                Conversation.participant_vendor_id == conv_data.participant_vendor_id,
                Conversation.service_type == conv_data.service_type,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    if conv_data.participant_vendor_id:
        vendor_result = await db.execute(
            select(Vendor).where(Vendor.id == conv_data.participant_vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=400, detail="Vendor not found")

    conversation = Conversation(
        participant_user_id=current_user.id,
        participant_vendor_id=conv_data.participant_vendor_id,
        service_type=conv_data.service_type,
        service_id=conv_data.service_id,
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return conversation


@router.get("/{conversation_id}", response_model=chat_schema.ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get conversation details"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # SECURITY: enforce participation (OWASP API1 BOLA)
    vendor = await get_participant_vendor(db, current_user)
    assert_conversation_participant(conversation, current_user, vendor)

    return conversation


@router.get(
    "/{conversation_id}/messages", response_model=list[chat_schema.MessageResponse]
)
async def get_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    before: uuid.UUID = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get conversation messages"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # SECURITY: enforce participation (OWASP API1 BOLA)
    vendor = await get_participant_vendor(db, current_user)
    assert_conversation_participant(conversation, current_user, vendor)

    query = select(Message).where(Message.conversation_id == conversation_id)

    if before:
        query = query.where(Message.id != before)

    result = await db.execute(query.order_by(desc(Message.created_at)).limit(limit))
    messages = result.scalars().all()

    return messages


@router.post("/{conversation_id}/messages", response_model=chat_schema.MessageResponse)
async def send_message(
    conversation_id: uuid.UUID,
    message_data: chat_schema.MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    vendor = await get_participant_vendor(db, current_user)

    # SECURITY: derive sender identity AFTER participation check (fixes
    # previous bypass where any vendor could post as "user" in conversations
    # they don't belong to)
    if vendor and conversation.participant_vendor_id == vendor.id:
        sender_type = "vendor"
        sender_id = vendor.id
    elif conversation.participant_user_id == current_user.id:
        sender_type = "user"
        sender_id = current_user.id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant of this conversation",
        )

    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        sender_type=sender_type,
        message_type=message_data.message_type,
        content=message_data.content,
        attachments=message_data.attachments,
    )

    conversation.last_message_at = datetime.now(timezone.utc)

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


@router.post("/{conversation_id}/read", response_model=MarkReadResponse)
async def mark_read(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark messages as read"""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # SECURITY: enforce participation (OWASP API1 BOLA)
    vendor = await get_participant_vendor(db, current_user)
    assert_conversation_participant(conversation, current_user, vendor)

    result = await db.execute(
        select(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != current_user.id,
            Message.read_at.is_(None),
        )
    )
    messages = result.scalars().all()

    for message in messages:
        message.read_at = datetime.now(timezone.utc)

    await db.commit()

    return {"message": "Marked as read", "count": len(messages)}
