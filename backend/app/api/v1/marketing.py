"""
Marketing API Endpoints for BillionMail Integration
Handles email campaigns, templates, and analytics
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin, require_role, get_current_user
from app.models import User, UserRole, Vendor
from app.models.marketing import (
    EmailCampaign,
    EmailTemplate,
    CampaignStatus,
    CampaignType,
    InboxMessage,
    EmailPreference,
)
from app.services.billionmail import MarketingService

router = APIRouter(tags=["Marketing"])


# ============ Dependencies ============


async def get_current_vendor(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
) -> "Vendor":
    """Get the current vendor from the authenticated user"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor not found")
    return vendor


# ============ Pydantic Schemas ============


def validate_html_content(v: str) -> str:
    """Validate HTML content for potentially dangerous tags/scripts."""
    import re

    # Check for potentially dangerous tags
    dangerous_tags = re.compile(
        r"<\s*(script|iframe|object|embed|form|input)", re.IGNORECASE
    )
    event_handlers = re.compile(r"on\w+\s*=", re.IGNORECASE)
    javascript_protocol = re.compile(r"javascript:", re.IGNORECASE)

    if dangerous_tags.search(v):
        raise ValueError(
            "HTML content contains potentially dangerous tags (script, iframe, etc.)"
        )
    if event_handlers.search(v):
        raise ValueError("HTML content contains event handlers (onclick, etc.)")
    if javascript_protocol.search(v):
        raise ValueError("HTML content contains javascript: protocol")
    return v


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=255)
    campaign_type: str = Field(default="newsletter")
    html_content: str = Field(..., min_length=10)
    recipient_type: str = Field(default="all_users")
    template_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    from_name: str = Field(default="Costa Rica Travel")
    from_email: str = Field(default="noreply@costaricatravel.dev")

    @field_validator("html_content")
    @classmethod
    def validate_html(cls, v: str) -> str:
        return validate_html_content(v)


class CampaignResponse(BaseModel):
    id: UUID
    name: str
    subject: str
    campaign_type: str
    status: str
    recipient_type: str
    total_recipients: int
    sent_count: int
    open_rate: float
    click_rate: float
    created_at: datetime
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class CampaignDetailResponse(CampaignResponse):
    html_content: Optional[str]
    from_name: str
    from_email: str


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_type: str = Field(default="newsletter")
    html_content: str = Field(..., min_length=10)


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    template_type: str
    is_system: bool
    preview_image: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignAnalytics(BaseModel):
    campaign_id: str
    campaign_name: str
    total_recipients: int
    sent: int
    delivered: int
    opened: int
    clicked: int
    bounced: int
    open_rate: float
    click_rate: float
    click_to_open_rate: float


class SendCampaignRequest(BaseModel):
    test_email: Optional[str] = None  # Send test first


class InboxMessageCreate(BaseModel):
    vendor_id: Optional[UUID] = None
    subject: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    message_type: str = Field(default="inquiry")
    booking_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    tour_id: Optional[UUID] = None


class InboxMessageResponse(BaseModel):
    id: UUID
    subject: str
    content: str
    is_from_customer: bool
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Response schemas for endpoints
class SendCampaignResponse(BaseModel):
    message: str
    total: int
    sent: int
    failed: int


class MarketingOverviewResponse(BaseModel):
    campaigns: dict
    engagement: dict
    recent_campaigns: list[dict]


class VendorAnalyticsResponse(BaseModel):
    total_campaigns: int
    total_recipients: int
    total_opens: int
    total_clicks: int
    engagement_rate: float


class InboxMessageItem(BaseModel):
    id: str
    subject: str
    content: str
    is_from_customer: bool
    is_read: bool
    created_at: str
    vendor_id: Optional[str] = None


class InboxResponse(BaseModel):
    messages: list[InboxMessageItem]
    unread_count: int
    total: int


class SendInboxResponse(BaseModel):
    message: str
    message_id: str


class UnreadCountResponse(BaseModel):
    unread_count: int


class EmailPreferencesResponse(BaseModel):
    marketing_emails: bool
    booking_notifications: bool
    promotional_emails: bool
    newsletter: bool
    email_frequency: Optional[str] = None
    unsubscribed_all: bool
    vendor_preferences: dict
    categories: dict


class UpdatePreferencesResponse(BaseModel):
    message: str


# ============ Super Admin Endpoints ============


@router.get("/admin/campaigns", response_model=List[CampaignResponse])
async def list_all_campaigns(
    status: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    List all email campaigns (Super Admin only)
    """
    query = select(EmailCampaign).order_by(desc(EmailCampaign.created_at))

    if status:
        query = query.where(EmailCampaign.status == status)
    if campaign_type:
        query = query.where(EmailCampaign.campaign_type == campaign_type)

    # Eager load relationships to avoid N+1
    query = query.options(
        joinedload(EmailCampaign.creator),
        joinedload(EmailCampaign.vendor),
        joinedload(EmailCampaign.template),
    )

    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    campaigns = result.scalars().all()

    return campaigns


@router.post("/admin/campaigns", response_model=CampaignResponse)
@limiter.limit("10/minute")
async def create_admin_campaign(
    request: Request,
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Create a new marketing campaign (Super Admin)
    """
    service = MarketingService(db)

    campaign = await service.create_campaign(
        name=data.name,
        subject=data.subject,
        campaign_type=data.campaign_type,
        html_content=data.html_content,
        recipient_type=data.recipient_type,
        created_by=str(current_user.id),
        template_id=data.template_id,
        scheduled_at=data.scheduled_at,
        from_name=data.from_name,
        from_email=data.from_email,
    )

    return campaign


@router.post("/admin/campaigns/{campaign_id}/send", response_model=SendCampaignResponse)
@limiter.limit("5/minute")
async def send_admin_campaign(
    request: Request,
    campaign_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Send a campaign immediately (Super Admin)
    """
    service = MarketingService(db)

    result = await service.send_campaign(str(campaign_id))

    if not result["success"]:
        raise HTTPException(
            status_code=400, detail=result.get("error", "Failed to send campaign")
        )

    return {
        "message": "Campaign sent successfully",
        "total": result["total"],
        "sent": result["sent"],
        "failed": result["failed"],
    }


@router.get(
    "/admin/campaigns/{campaign_id}/analytics", response_model=CampaignAnalytics
)
async def get_campaign_analytics(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get detailed analytics for a campaign
    """
    service = MarketingService(db)
    analytics = await service.get_campaign_analytics(str(campaign_id))

    if not analytics:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return analytics


@router.get("/admin/templates", response_model=List[TemplateResponse])
async def list_templates(
    template_type: Optional[str] = Query(None),
    include_system: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    List email templates (Super Admin)
    """
    query = select(EmailTemplate)

    if template_type:
        query = query.where(EmailTemplate.template_type == template_type)
    if not include_system:
        query = query.where(EmailTemplate.is_system == False)

    query = query.order_by(desc(EmailTemplate.created_at))

    result = await db.execute(query)
    templates = result.scalars().all()

    return templates


@router.post("/admin/templates", response_model=TemplateResponse)
@limiter.limit("10/minute")
async def create_template(
    request: Request,
    data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Create a new email template (Super Admin)
    """
    template = EmailTemplate(
        name=data.name,
        description=data.description,
        template_type=getattr(
            CampaignType, data.template_type.upper(), CampaignType.NEWSLETTER
        ),
        html_content=data.html_content,
        text_content=MarketingService(db).mail_service._strip_html(data.html_content),
        is_system=False,
        created_by=current_user.id,
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    return template


@router.get("/admin/analytics/overview", response_model=MarketingOverviewResponse)
async def get_marketing_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get overall marketing analytics (Super Admin)
    """
    # Campaign stats
    campaigns_result = await db.execute(
        select(
            func.count(EmailCampaign.id).label("total"),
            func.count(EmailCampaign.id)
            .filter(EmailCampaign.status == CampaignStatus.SENT)
            .label("sent"),
            func.sum(EmailCampaign.total_recipients).label("total_recipients"),
            func.sum(EmailCampaign.sent_count).label("total_sent"),
            func.sum(EmailCampaign.opened_count).label("total_opens"),
            func.sum(EmailCampaign.clicked_count).label("total_clicks"),
        )
    )
    campaigns_stats = campaigns_result.one()

    # Recent campaigns
    recent_campaigns = await db.execute(
        select(EmailCampaign).order_by(desc(EmailCampaign.created_at)).limit(5)
    )

    return {
        "campaigns": {
            "total": campaigns_stats.total or 0,
            "sent": campaigns_stats.sent or 0,
            "draft": campaigns_stats.total - campaigns_stats.sent
            if campaigns_stats.total
            else 0,
        },
        "engagement": {
            "total_recipients": campaigns_stats.total_recipients or 0,
            "total_sent": campaigns_stats.total_sent or 0,
            "total_opens": campaigns_stats.total_opens or 0,
            "total_clicks": campaigns_stats.total_clicks or 0,
            "avg_open_rate": round(
                (campaigns_stats.total_opens or 0)
                / (campaigns_stats.total_sent or 1)
                * 100,
                2,
            ),
            "avg_click_rate": round(
                (campaigns_stats.total_clicks or 0)
                / (campaigns_stats.total_sent or 1)
                * 100,
                2,
            ),
        },
        "recent_campaigns": [
            {
                "id": str(c.id),
                "name": c.name,
                "status": c.status.value,
                "recipients": c.total_recipients,
                "created_at": c.created_at.isoformat(),
            }
            for c in recent_campaigns.scalars().all()
        ],
    }


# ============ Vendor Endpoints ============


@router.get("/vendor/campaigns", response_model=List[CampaignResponse])
async def list_vendor_campaigns(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    vendor=Depends(get_current_vendor),
):
    """
    List vendor's own email campaigns
    """
    query = (
        select(EmailCampaign)
        .where(EmailCampaign.vendor_id == vendor.id)
        .order_by(desc(EmailCampaign.created_at))
    )

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    campaigns = result.scalars().all()

    return campaigns


@router.post("/vendor/campaigns", response_model=CampaignResponse)
@limiter.limit("10/minute")
async def create_vendor_campaign(
    request: Request,
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
    vendor=Depends(get_current_vendor),
):
    """
    Create a new campaign for vendor's customers
    """
    service = MarketingService(db)

    campaign = await service.create_campaign(
        name=data.name,
        subject=data.subject,
        campaign_type="promotion",  # Vendors can only send promotions
        html_content=data.html_content,
        recipient_type="vendor_customers",  # Only their customers
        created_by=str(current_user.id),
        vendor_id=str(vendor.id),
        template_id=data.template_id,
        scheduled_at=data.scheduled_at,
        from_name=vendor.business_name or data.from_name,
        from_email=data.from_email,
    )

    return campaign


@router.get("/vendor/analytics", response_model=VendorAnalyticsResponse)
async def get_vendor_analytics(
    db: AsyncSession = Depends(get_db), vendor=Depends(get_current_vendor)
):
    """
    Get analytics for vendor's campaigns
    """
    # Get vendor campaign stats
    stats_result = await db.execute(
        select(
            func.count(EmailCampaign.id).label("total"),
            func.sum(EmailCampaign.total_recipients).label("recipients"),
            func.sum(EmailCampaign.opened_count).label("opens"),
            func.sum(EmailCampaign.clicked_count).label("clicks"),
        ).where(EmailCampaign.vendor_id == vendor.id)
    )
    stats = stats_result.one()

    return {
        "total_campaigns": stats.total or 0,
        "total_recipients": stats.recipients or 0,
        "total_opens": stats.opens or 0,
        "total_clicks": stats.clicks or 0,
        "engagement_rate": round(
            (stats.clicks or 0) / (stats.recipients or 1) * 100, 2
        ),
    }


@router.post("/vendor/campaigns/{campaign_id}/send", response_model=SendCampaignResponse)
@limiter.limit("5/minute")
async def send_vendor_campaign(
    request: Request,
    campaign_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
    vendor=Depends(get_current_vendor),
):
    """
    Send a campaign immediately (Vendor)
    """
    # Verify campaign belongs to this vendor
    result = await db.execute(
        select(EmailCampaign).where(
            EmailCampaign.id == campaign_id,
            EmailCampaign.vendor_id == vendor.id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    service = MarketingService(db)
    send_result = await service.send_campaign(str(campaign_id))

    if not send_result["success"]:
        raise HTTPException(
            status_code=400, detail=send_result.get("error", "Failed to send campaign")
        )

    return {
        "message": "Campaign sent successfully",
        "total": send_result["total"],
        "sent": send_result["sent"],
        "failed": send_result["failed"],
    }


# ============ Inbox Endpoints ============


@router.get("/inbox", response_model=InboxResponse)
async def get_user_inbox(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's inbox messages
    """
    query = select(InboxMessage).where(InboxMessage.customer_id == current_user.id)

    if unread_only:
        query = query.where(InboxMessage.is_read == False)

    query = query.order_by(desc(InboxMessage.created_at))

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    # Get unread count
    unread_count_result = await db.execute(
        select(func.count(InboxMessage.id))
        .where(InboxMessage.customer_id == current_user.id)
        .where(InboxMessage.is_read == False)
    )
    unread_count = unread_count_result.scalar() or 0

    return {
        "messages": [
            {
                "id": str(m.id),
                "subject": m.subject,
                "content": m.content[:200] + "..."
                if len(m.content) > 200
                else m.content,
                "is_from_customer": m.is_from_customer,
                "is_read": m.is_read,
                "created_at": m.created_at.isoformat(),
                "vendor_id": str(m.vendor_id) if m.vendor_id else None,
            }
            for m in messages
        ],
        "unread_count": unread_count,
        "total": len(messages),
    }


@router.post("/inbox/send", response_model=SendInboxResponse)
@limiter.limit("10/minute")
async def send_inbox_message(
    request: Request,
    data: InboxMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to a vendor or support
    """
    import uuid

    message = InboxMessage(
        id=uuid.uuid4(),
        customer_id=current_user.id,
        vendor_id=data.vendor_id,
        thread_id=uuid.uuid4(),  # New thread
        subject=data.subject,
        content=data.content,
        message_type=data.message_type,
        booking_id=data.booking_id,
        property_id=data.property_id,
        tour_id=data.tour_id,
        is_from_customer=True,
        is_read=False,
    )

    db.add(message)
    await db.commit()

    return {"message": "Message sent successfully", "message_id": str(message.id)}


@router.get("/inbox/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get unread message count
    """
    result = await db.execute(
        select(func.count(InboxMessage.id))
        .where(InboxMessage.customer_id == current_user.id)
        .where(InboxMessage.is_read == False)
    )
    count = result.scalar() or 0

    return {"unread_count": count}


# ============ Email Preferences ============


@router.get("/preferences", response_model=EmailPreferencesResponse)
async def get_email_preferences(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Get user's email preferences
    """
    result = await db.execute(
        select(EmailPreference).where(EmailPreference.user_id == current_user.id)
    )
    prefs = result.scalar_one_or_none()

    if not prefs:
        # Create default preferences
        prefs = EmailPreference(user_id=current_user.id)
        db.add(prefs)
        await db.commit()

    return {
        "marketing_emails": prefs.marketing_emails,
        "booking_notifications": prefs.booking_notifications,
        "promotional_emails": prefs.promotional_emails,
        "newsletter": prefs.newsletter,
        "email_frequency": prefs.email_frequency,
        "unsubscribed_all": prefs.unsubscribed_all,
        "vendor_preferences": prefs.vendor_preferences or {},
        "categories": prefs.categories or {},
    }


@router.put("/preferences", response_model=UpdatePreferencesResponse)
@limiter.limit("10/minute")
async def update_email_preferences(
    request: Request,
    prefs: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update email preferences
    """
    result = await db.execute(
        select(EmailPreference).where(EmailPreference.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if not existing:
        existing = EmailPreference(user_id=current_user.id)
        db.add(existing)

    # Update fields
    if "marketing_emails" in prefs:
        existing.marketing_emails = prefs["marketing_emails"]
    if "booking_notifications" in prefs:
        existing.booking_notifications = prefs["booking_notifications"]
    if "promotional_emails" in prefs:
        existing.promotional_emails = prefs["promotional_emails"]
    if "newsletter" in prefs:
        existing.newsletter = prefs["newsletter"]
    if "email_frequency" in prefs:
        existing.email_frequency = prefs["email_frequency"]
    if "vendor_preferences" in prefs:
        existing.vendor_preferences = prefs["vendor_preferences"]
    if "categories" in prefs:
        existing.categories = prefs["categories"]

    await db.commit()

    return {"message": "Preferences updated successfully"}
