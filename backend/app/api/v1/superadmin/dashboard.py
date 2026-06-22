"""
Super Admin Dashboard endpoints.
Provides comprehensive overview metrics and real-time system status.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import require_superadmin
from app.models import (
    User,
    UserRole,
    Vendor,
    VendorStatus,
    Booking,
    BookingStatus,
    Property,
    Tour,
    Review,
    BlogPost,
    BlogPostStatus,
    Destination,
    NewsletterSubscriber,
)

router = APIRouter()


# Response Models
class DashboardStats(BaseModel):
    """Comprehensive dashboard statistics."""

    # User metrics
    total_users: int
    users_by_role: dict
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    active_users_today: int

    # Vendor metrics
    total_vendors: int
    pending_vendors: int
    active_vendors: int
    suspended_vendors: int

    # Booking metrics
    total_bookings: int
    total_revenue: float
    net_revenue: float  # After commissions
    bookings_today: int
    bookings_this_week: int
    bookings_this_month: int
    revenue_today: float
    revenue_this_month: float

    # Content metrics
    total_properties: int
    total_tours: int
    total_reviews: int
    average_rating: float
    total_blog_posts: int
    published_blog_posts: int
    total_destinations: int

    # Newsletter metrics
    newsletter_subscribers: int
    newsletter_subscribers_today: int
    newsletter_subscribers_this_week: int
    newsletter_subscribers_this_month: int

    # System health (placeholder values - would integrate with monitoring)
    system_health: dict


class RecentActivityItem(BaseModel):
    """Single activity item for recent activity feed."""

    id: str
    action: str
    entity_type: str
    entity_name: Optional[str]
    user_name: str
    user_email: str
    timestamp: datetime
    description: str


class AlertItem(BaseModel):
    """System alert item."""

    id: str
    severity: str  # info, warning, critical
    title: str
    description: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    created_at: datetime
    is_resolved: bool


class RecentActivityResponse(BaseModel):
    """Response model for recent activity endpoint."""

    id: str
    action: str
    entity_type: str
    entity_name: Optional[str]
    user_name: str
    user_email: str
    timestamp: datetime
    description: str


class AlertResponse(BaseModel):
    """Response model for system alerts."""

    id: str
    severity: str
    title: str
    description: str
    entity_type: Optional[str]
    entity_id: Optional[str]
    created_at: datetime
    is_resolved: bool


class RevenueTrendPoint(BaseModel):
    date: str
    revenue: float
    bookings_count: int


class RevenueTrendResponse(BaseModel):
    period_days: int
    start_date: str
    end_date: str
    data: list[RevenueTrendPoint]


class NewsletterStatsResponse(BaseModel):
    total_subscribers: int
    active_subscribers: int
    confirmed_subscribers: int
    unconfirmed: int
    new_today: int
    new_this_week: int
    new_this_month: int
    by_source: dict
    conversion_rate: float


class TopContentResponse(BaseModel):
    featured_destinations: list[dict]
    top_tours: list[dict]
    top_properties: list[dict]


class QuickAction(BaseModel):
    id: str
    label: str
    count: int
    icon: str
    href: str
    priority: str


class QuickActionsResponse(BaseModel):
    actions: list[QuickAction]


class TopVendorItem(BaseModel):
    vendor_id: str
    vendor_name: str
    logo_url: Optional[str]
    total_bookings: int
    total_revenue: float


class SystemMetricsResponse(BaseModel):
    timestamp: str
    database: dict
    system: dict
    api: dict


# Dashboard Overview
@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get comprehensive dashboard statistics for Super Admin.
    Includes user metrics, vendor status, bookings, revenue, and content stats.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start.replace(day=1)

    # User statistics
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    # Users by role
    users_by_role = {}
    for role in UserRole:
        count_result = await db.execute(
            select(func.count(User.id)).where(User.role == role)
        )
        users_by_role[role.value] = count_result.scalar() or 0

    # New users today/week/month
    new_today_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )
    new_users_today = new_today_result.scalar() or 0

    new_week_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_start)
    )
    new_users_this_week = new_week_result.scalar() or 0

    new_month_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= month_start)
    )
    new_users_this_month = new_month_result.scalar() or 0

    # Active users today (simplified - users who logged in)
    active_today_result = await db.execute(
        select(func.count(User.id)).where(User.last_login >= today_start)
    )
    active_users_today = active_today_result.scalar() or 0

    # Vendor statistics
    total_vendors_result = await db.execute(select(func.count(Vendor.id)))
    total_vendors = total_vendors_result.scalar() or 0

    pending_vendors_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.PENDING)
    )
    pending_vendors = pending_vendors_result.scalar() or 0

    active_vendors_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.ACTIVE)
    )
    active_vendors = active_vendors_result.scalar() or 0

    suspended_vendors_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.SUSPENDED)
    )
    suspended_vendors = suspended_vendors_result.scalar() or 0

    # Booking statistics
    total_bookings_result = await db.execute(select(func.count(Booking.id)))
    total_bookings = total_bookings_result.scalar() or 0

    # Revenue calculations
    total_revenue_result = await db.execute(
        select(func.coalesce(func.sum(Booking.total_amount), 0))
    )
    total_revenue = float(total_revenue_result.scalar() or 0)
    net_revenue = total_revenue * 0.90  # Assuming 10% commission

    # Bookings today/week/month
    bookings_today_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.created_at >= today_start)
    )
    bookings_today = bookings_today_result.scalar() or 0

    bookings_week_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.created_at >= week_start)
    )
    bookings_this_week = bookings_week_result.scalar() or 0

    bookings_month_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.created_at >= month_start)
    )
    bookings_this_month = bookings_month_result.scalar() or 0

    # Revenue today/month
    revenue_today_result = await db.execute(
        select(func.coalesce(func.sum(Booking.total_amount), 0)).where(
            Booking.created_at >= today_start
        )
    )
    revenue_today = float(revenue_today_result.scalar() or 0)

    revenue_month_result = await db.execute(
        select(func.coalesce(func.sum(Booking.total_amount), 0)).where(
            Booking.created_at >= month_start
        )
    )
    revenue_this_month = float(revenue_month_result.scalar() or 0)

    # Content statistics
    total_properties_result = await db.execute(select(func.count(Property.id)))
    total_properties = total_properties_result.scalar() or 0

    total_tours_result = await db.execute(select(func.count(Tour.id)))
    total_tours = total_tours_result.scalar() or 0

    total_reviews_result = await db.execute(select(func.count(Review.id)))
    total_reviews = total_reviews_result.scalar() or 0

    average_rating_result = await db.execute(
        select(func.coalesce(func.avg(Review.rating), 0))
    )
    average_rating = float(average_rating_result.scalar() or 0)

    total_blog_posts_result = await db.execute(select(func.count(BlogPost.id)))
    total_blog_posts = total_blog_posts_result.scalar() or 0

    published_blog_posts_result = await db.execute(
        select(func.count(BlogPost.id)).where(
            BlogPost.status == BlogPostStatus.PUBLISHED
        )
    )
    published_blog_posts = published_blog_posts_result.scalar() or 0

    total_destinations_result = await db.execute(select(func.count(Destination.id)))
    total_destinations = total_destinations_result.scalar() or 0

    # Newsletter statistics
    newsletter_total_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.is_active
        )
    )
    newsletter_subscribers = newsletter_total_result.scalar() or 0

    newsletter_today_result = await db.execute(
        select(func.count(NewsletterSubscriber.id))
        .where(NewsletterSubscriber.created_at >= today_start)
        .where(NewsletterSubscriber.is_active)
    )
    newsletter_subscribers_today = newsletter_today_result.scalar() or 0

    newsletter_week_result = await db.execute(
        select(func.count(NewsletterSubscriber.id))
        .where(NewsletterSubscriber.created_at >= week_start)
        .where(NewsletterSubscriber.is_active)
    )
    newsletter_subscribers_this_week = newsletter_week_result.scalar() or 0

    newsletter_month_result = await db.execute(
        select(func.count(NewsletterSubscriber.id))
        .where(NewsletterSubscriber.created_at >= month_start)
        .where(NewsletterSubscriber.is_active)
    )
    newsletter_subscribers_this_month = newsletter_month_result.scalar() or 0

    # System health (would integrate with actual monitoring in production)
    system_health = {
        "api_status": "operational",
        "database_status": "connected",
        "response_time_ms": 45,
        "error_rate": 0.02,
        "last_backup": (now - timedelta(hours=2)).isoformat(),
    }

    return DashboardStats(
        total_users=total_users,
        users_by_role=users_by_role,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        new_users_this_month=new_users_this_month,
        active_users_today=active_users_today,
        total_vendors=total_vendors,
        pending_vendors=pending_vendors,
        active_vendors=active_vendors,
        suspended_vendors=suspended_vendors,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        net_revenue=net_revenue,
        bookings_today=bookings_today,
        bookings_this_week=bookings_this_week,
        bookings_this_month=bookings_this_month,
        revenue_today=revenue_today,
        revenue_this_month=revenue_this_month,
        total_properties=total_properties,
        total_tours=total_tours,
        total_reviews=total_reviews,
        average_rating=round(average_rating, 2),
        total_blog_posts=total_blog_posts,
        published_blog_posts=published_blog_posts,
        total_destinations=total_destinations,
        newsletter_subscribers=newsletter_subscribers,
        newsletter_subscribers_today=newsletter_subscribers_today,
        newsletter_subscribers_this_week=newsletter_subscribers_this_week,
        newsletter_subscribers_this_month=newsletter_subscribers_this_month,
        system_health=system_health,
    )


@router.get("/recent-activity", response_model=list[RecentActivityResponse])
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get recent activity across the platform.
    Returns recent bookings, user registrations, vendor approvals, etc.
    """
    # This is a simplified version - in production would query audit_logs
    # For now, we'll return recent bookings as activity
    from sqlalchemy import desc

    result = await db.execute(
        select(Booking, User, Vendor)
        .join(User, Booking.user_id == User.id)
        .join(Vendor, Booking.vendor_id == Vendor.id)
        .order_by(desc(Booking.created_at))
        .limit(limit)
    )

    activities = []
    for booking, user, vendor in result.all():
        activities.append(
            {
                "id": str(booking.id),
                "action": "booking_created",
                "entity_type": "booking",
                "entity_name": f"Reserva #{str(booking.id)[:8]}",
                "user_name": user.full_name,
                "user_email": user.email,
                "timestamp": booking.created_at,
                "description": f"Nueva reserva de ${booking.total_amount} para {vendor.business_name}",
            }
        )

    return activities


@router.get("/alerts", response_model=list[AlertResponse])
async def get_system_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get system alerts that require Super Admin attention.
    Includes pending vendors, failed bookings, system issues, etc.
    """
    alerts = []
    now = datetime.now(timezone.utc)

    # Check for pending vendors
    pending_vendors_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.PENDING)
    )
    pending_count = pending_vendors_result.scalar() or 0

    if pending_count > 0:
        alerts.append(
            {
                "id": "pending_vendors",
                "severity": "warning" if pending_count < 5 else "critical",
                "title": f"{pending_count} proveedores pendientes de aprobación",
                "description": "Hay proveedores esperando revisión y aprobación.",
                "entity_type": "vendor",
                "entity_id": None,
                "created_at": now,
                "is_resolved": False,
            }
        )

    # Check for pending bookings
    pending_bookings_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
    )
    pending_bookings = pending_bookings_result.scalar() or 0

    if pending_bookings > 10:
        alerts.append(
            {
                "id": "pending_bookings",
                "severity": "warning",
                "title": f"{pending_bookings} reservas pendientes",
                "description": "Hay reservas que requieren atención o confirmación.",
                "entity_type": "booking",
                "entity_id": None,
                "created_at": now,
                "is_resolved": False,
            }
        )

    # Check for users without email verification
    unverified_result = await db.execute(
        select(func.count(User.id)).where(User.is_verified == False)
    )
    unverified_count = unverified_result.scalar() or 0

    if unverified_count > 50:
        alerts.append(
            {
                "id": "unverified_users",
                "severity": "info",
                "title": f"{unverified_count} usuarios sin verificar",
                "description": "Considera enviar recordatorios de verificación de email.",
                "entity_type": "user",
                "entity_id": None,
                "created_at": now,
                "is_resolved": False,
            }
        )

    return alerts


@router.get("/revenue-trend", response_model=RevenueTrendResponse)
async def get_revenue_trend(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get daily revenue trend for the specified period.
    """
    from sqlalchemy import func, cast, Date

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    result = await db.execute(
        select(
            cast(Booking.created_at, Date).label("date"),
            func.coalesce(func.sum(Booking.total_amount), 0).label("revenue"),
            func.count(Booking.id).label("bookings_count"),
        )
        .where(Booking.created_at >= start_date)
        .where(Booking.created_at <= end_date)
        .group_by(cast(Booking.created_at, Date))
        .order_by(cast(Booking.created_at, Date))
    )

    trend = []
    for row in result.all():
        trend.append(
            {
                "date": row.date.isoformat(),
                "revenue": float(row.revenue),
                "bookings_count": row.bookings_count,
            }
        )

    return {
        "period_days": days,
        "start_date": start_date.date().isoformat(),
        "end_date": end_date.date().isoformat(),
        "data": trend,
    }


@router.get("/newsletter-stats", response_model=NewsletterStatsResponse)
async def get_newsletter_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get detailed newsletter subscription statistics.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start.replace(day=1)

    # Total subscribers
    total_result = await db.execute(select(func.count(NewsletterSubscriber.id)))
    total = total_result.scalar() or 0

    # Active subscribers
    active_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.is_active
        )
    )
    active = active_result.scalar() or 0

    # Confirmed subscribers
    confirmed_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.is_confirmed
        )
    )
    confirmed = confirmed_result.scalar() or 0

    # New today
    new_today_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.created_at >= today_start
        )
    )
    new_today = new_today_result.scalar() or 0

    # New this week
    new_week_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.created_at >= week_start
        )
    )
    new_week = new_week_result.scalar() or 0

    # New this month
    new_month_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.created_at >= month_start
        )
    )
    new_month = new_month_result.scalar() or 0

    # By source
    sources_result = await db.execute(
        select(
            NewsletterSubscriber.source, func.count(NewsletterSubscriber.id)
        ).group_by(NewsletterSubscriber.source)
    )
    by_source = {row[0]: row[1] for row in sources_result.all()}

    return {
        "total_subscribers": total,
        "active_subscribers": active,
        "confirmed_subscribers": confirmed,
        "unconfirmed": total - confirmed,
        "new_today": new_today,
        "new_this_week": new_week,
        "new_this_month": new_month,
        "by_source": by_source,
        "conversion_rate": round((confirmed / total * 100), 2) if total > 0 else 0,
    }


@router.get("/top-content", response_model=TopContentResponse)
async def get_top_content(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get top performing content: destinations, tours, properties.
    """
    # Top destinations by featured status
    from sqlalchemy import desc

    featured_destinations = await db.execute(
        select(Destination)
        .where(Destination.is_featured)
        .where(Destination.is_active)
        .order_by(desc(Destination.order))
        .limit(limit)
    )

    # Top tours by featured
    featured_tours = await db.execute(
        select(Tour, func.count(Review.id).label("review_count"))
        .outerjoin(Review, Review.tour_id == Tour.id)
        .where(Tour.is_featured)
        .where(Tour.is_active)
        .group_by(Tour.id)
        .order_by(desc("review_count"))
        .limit(limit)
    )

    # Top properties
    top_properties = await db.execute(
        select(Property, func.avg(Review.rating).label("avg_rating"))
        .outerjoin(Review, Review.property_id == Property.id)
        .where(Property.is_active)
        .group_by(Property.id)
        .order_by(desc("avg_rating"))
        .limit(limit)
    )

    return {
        "featured_destinations": [
            {"id": str(d.id), "name": d.name, "slug": d.slug, "region": d.region}
            for d in featured_destinations.scalars().all()
        ],
        "top_tours": [
            {
                "id": str(t.id),
                "title": t.title,
                "category": t.category,
                "price": t.base_price,
                "review_count": review_count,
            }
            for t, review_count in featured_tours.all()
        ],
        "top_properties": [
            {
                "id": str(p.id),
                "name": p.name,
                "type": p.property_type,
                "location": p.location,
                "rating": round(float(avg_rating or 0), 2),
            }
            for p, avg_rating in top_properties.all()
        ],
    }


@router.get("/quick-actions", response_model=QuickActionsResponse)
async def get_quick_actions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get available quick actions with counts for the Super Admin dashboard.
    """
    now = datetime.now(timezone.utc)

    # Pending vendors
    pending_vendors = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.status == VendorStatus.PENDING)
    )
    pending_vendors_count = pending_vendors.scalar() or 0

    # Pending bookings
    pending_bookings = await db.execute(
        select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
    )
    pending_bookings_count = pending_bookings.scalar() or 0

    # Draft blog posts
    draft_posts = await db.execute(
        select(func.count(BlogPost.id)).where(BlogPost.status == BlogPostStatus.DRAFT)
    )
    draft_posts_count = draft_posts.scalar() or 0

    # Unverified users (last 24h)
    unverified_users = await db.execute(
        select(func.count(User.id))
        .where(User.is_verified == False)
        .where(User.created_at >= now - timedelta(days=1))
    )
    unverified_count = unverified_users.scalar() or 0

    # Support tickets placeholder (would integrate with support system)
    support_tickets = 0  # Placeholder

    return {
        "actions": [
            {
                "id": "approve_vendors",
                "label": "Aprobar Proveedores",
                "count": pending_vendors_count,
                "icon": "store",
                "href": "/superadmin/vendors?status=pending",
                "priority": "high" if pending_vendors_count > 0 else "normal",
            },
            {
                "id": "review_bookings",
                "label": "Revisar Reservas",
                "count": pending_bookings_count,
                "icon": "calendar",
                "href": "/superadmin/bookings?status=pending",
                "priority": "high" if pending_bookings_count > 10 else "normal",
            },
            {
                "id": "publish_content",
                "label": "Publicar Blog",
                "count": draft_posts_count,
                "icon": "file-text",
                "href": "/superadmin/blog?status=draft",
                "priority": "normal",
            },
            {
                "id": "verify_users",
                "label": "Verificar Usuarios",
                "count": unverified_count,
                "icon": "users",
                "href": "/superadmin/users?verified=false",
                "priority": "normal",
            },
            {
                "id": "support_tickets",
                "label": "Tickets Soporte",
                "count": support_tickets,
                "icon": "help-circle",
                "href": "/superadmin/support",
                "priority": "normal",
            },
        ]
    }


@router.get("/top-vendors", response_model=list[TopVendorItem])
async def get_top_vendors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get top performing vendors by revenue and bookings.
    """
    from sqlalchemy import desc

    # Query to get vendor performance metrics
    query = (
        select(
            Vendor.id,
            Vendor.business_name,
            Vendor.logo_url,
            func.count(Booking.id).label("total_bookings"),
            func.sum(Booking.total_amount).label("total_revenue"),
        )
        .join(Booking, Booking.vendor_id == Vendor.id)
        .where(Booking.status == BookingStatus.CONFIRMED)
        .group_by(Vendor.id, Vendor.business_name, Vendor.logo_url)
        .order_by(desc("total_revenue"))
        .limit(limit)
    )

    result = await db.execute(query)
    vendors = result.all()

    return [
        {
            "vendor_id": str(v.id),
            "vendor_name": v.business_name,
            "logo_url": v.logo_url,
            "total_bookings": v.total_bookings or 0,
            "total_revenue": float(v.total_revenue or 0),
        }
        for v in vendors
    ]


@router.get("/system-metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get real-time system performance metrics.
    """
    import psutil

    # Database connection test
    db_start = datetime.now(timezone.utc)
    try:
        await db.execute(select(func.count(User.id)))
        db_response_time = (
            datetime.now(timezone.utc) - db_start
        ).total_seconds() * 1000
        db_status = "healthy"
    except (OSError, RuntimeError):
        db_response_time = 0
        db_status = "error"

    # System metrics
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        metrics = {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_mb": memory.available // (1024 * 1024),
            "disk_usage_percent": disk.percent,
            "disk_free_gb": disk.free // (1024 * 1024 * 1024),
        }
    except (OSError, RuntimeError, PermissionError):
        metrics = {
            "cpu_usage_percent": 0,
            "memory_usage_percent": 0,
            "memory_available_mb": 0,
            "disk_usage_percent": 0,
            "disk_free_gb": 0,
        }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "response_time_ms": round(db_response_time, 2),
            "connections_active": 0,  # Would need pg_stat_activity query
        },
        "system": metrics,
        "api": {
            "status": "operational",
            "uptime_seconds": 0,  # Would track from startup
            "requests_per_minute": 0,  # Would need request tracking
        },
    }
