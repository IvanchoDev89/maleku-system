"""
Super Admin Dashboard endpoints.
Provides comprehensive overview metrics and real-time system status.
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_superadmin
from app.models import (
    BlogPost,
    BlogPostStatus,
    Booking,
    BookingStatus,
    Destination,
    NewsletterSubscriber,
    Property,
    Review,
    Tour,
    User,
    UserRole,
    Vendor,
    VendorStatus,
)

router = APIRouter(tags=["SuperAdmin - Dashboard"])


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
    entity_name: str | None
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
    entity_type: str | None
    entity_id: str | None
    created_at: datetime
    is_resolved: bool


class RecentActivityResponse(BaseModel):
    """Response model for recent activity endpoint."""

    id: str
    action: str
    entity_type: str
    entity_name: str | None
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
    entity_type: str | None
    entity_id: str | None
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
    logo_url: str | None
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
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start.replace(day=1)

    # === Consolidated user statistics (1 query replaces 9) ===
    user_row = (
        await db.execute(
            select(
                func.count(User.id).label("total"),
                func.count(User.id).filter(User.role == UserRole.SUPER_ADMIN).label("super_admin"),
                func.count(User.id).filter(User.role == UserRole.ADMIN).label("admin"),
                func.count(User.id).filter(User.role == UserRole.VENDOR).label("vendor"),
                func.count(User.id).filter(User.role == UserRole.CLIENT).label("client"),
                func.count(User.id).filter(User.role == UserRole.AGENT).label("agent"),
                func.count(User.id)
                .filter(User.role == UserRole.CUSTOMER_SERVICE)
                .label("customer_service"),
                func.count(User.id).filter(User.created_at >= today_start).label("new_today"),
                func.count(User.id).filter(User.created_at >= week_start).label("new_week"),
                func.count(User.id).filter(User.created_at >= month_start).label("new_month"),
                func.count(User.id).filter(User.last_login >= today_start).label("active_today"),
            )
        )
    ).one()
    total_users = user_row.total
    users_by_role = {
        "super_admin": user_row.super_admin,
        "admin": user_row.admin,
        "vendor": user_row.vendor,
        "client": user_row.client,
        "agent": user_row.agent,
        "customer_service": user_row.customer_service,
    }
    new_users_today = user_row.new_today
    new_users_this_week = user_row.new_week
    new_users_this_month = user_row.new_month
    active_users_today = user_row.active_today

    # === Consolidated vendor statistics (1 query replaces 4) ===
    vendor_row = (
        await db.execute(
            select(
                func.count(Vendor.id).label("total"),
                func.count(Vendor.id)
                .filter(Vendor.status == VendorStatus.PENDING)
                .label("pending"),
                func.count(Vendor.id).filter(Vendor.status == VendorStatus.ACTIVE).label("active"),
                func.count(Vendor.id)
                .filter(Vendor.status == VendorStatus.SUSPENDED)
                .label("suspended"),
            )
        )
    ).one()
    total_vendors = vendor_row.total
    pending_vendors = vendor_row.pending
    active_vendors = vendor_row.active
    suspended_vendors = vendor_row.suspended

    # === Consolidated booking + revenue statistics (1 query replaces 7) ===
    booking_row = (
        await db.execute(
            select(
                func.count(Booking.id).label("total"),
                func.count(Booking.id).filter(Booking.created_at >= today_start).label("today"),
                func.count(Booking.id).filter(Booking.created_at >= week_start).label("week"),
                func.count(Booking.id).filter(Booking.created_at >= month_start).label("month"),
                func.coalesce(func.sum(Booking.total_amount), 0).label("revenue_total"),
                func.coalesce(
                    func.sum(Booking.total_amount).filter(Booking.created_at >= today_start), 0
                ).label("revenue_today"),
                func.coalesce(
                    func.sum(Booking.total_amount).filter(Booking.created_at >= month_start), 0
                ).label("revenue_month"),
            )
        )
    ).one()
    total_bookings = booking_row.total
    bookings_today = booking_row.today
    bookings_this_week = booking_row.week
    bookings_this_month = booking_row.month
    total_revenue = float(booking_row.revenue_total)
    revenue_today = float(booking_row.revenue_today)
    revenue_this_month = float(booking_row.revenue_month)
    net_revenue = total_revenue * 0.90

    # === Consolidated content statistics (1 query replaces 8) ===
    content_row = (
        await db.execute(
            select(
                func.count(Property.id).label("properties"),
                func.count(Tour.id).label("tours"),
                func.count(Review.id).label("reviews"),
                func.coalesce(func.avg(Review.rating), 0).label("avg_rating"),
                func.count(BlogPost.id).label("blog_posts"),
                func.count(BlogPost.id)
                .filter(BlogPost.status == BlogPostStatus.PUBLISHED)
                .label("published_posts"),
                func.count(Destination.id).label("destinations"),
            )
        )
    ).one()
    total_properties = content_row.properties
    total_tours = content_row.tours
    total_reviews = content_row.reviews
    average_rating = float(content_row.avg_rating)
    total_blog_posts = content_row.blog_posts
    published_blog_posts = content_row.published_posts
    total_destinations = content_row.destinations

    # === Consolidated newsletter statistics (2 queries replace 7) ===
    ns_row = (
        await db.execute(
            select(
                func.count(NewsletterSubscriber.id).label("total"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.is_active)
                .label("active"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.is_confirmed)
                .label("confirmed"),
                func.count(NewsletterSubscriber.id)
                .filter(
                    NewsletterSubscriber.created_at >= today_start, NewsletterSubscriber.is_active
                )
                .label("new_today"),
                func.count(NewsletterSubscriber.id)
                .filter(
                    NewsletterSubscriber.created_at >= week_start, NewsletterSubscriber.is_active
                )
                .label("new_week"),
                func.count(NewsletterSubscriber.id)
                .filter(
                    NewsletterSubscriber.created_at >= month_start, NewsletterSubscriber.is_active
                )
                .label("new_month"),
            )
        )
    ).one()
    newsletter_subscribers = ns_row.active
    newsletter_subscribers_today = ns_row.new_today
    newsletter_subscribers_this_week = ns_row.new_week
    newsletter_subscribers_this_month = ns_row.new_month

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
    now = datetime.now(UTC)

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


@router.post("/alerts/{alert_id}/dismiss")
async def dismiss_alert(
    alert_id: str,
    current_user: User = Depends(require_superadmin()),
):
    """
    Dismiss a system alert.
    Alerts are ephemeral and regenerated on each request,
    so this simply acknowledges the dismissal. The alert
    will reappear if the underlying condition persists.
    """
    return {"status": "dismissed", "alert_id": alert_id}


@router.get("/revenue-trend", response_model=RevenueTrendResponse)
async def get_revenue_trend(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get daily revenue trend for the specified period.
    """
    from sqlalchemy import Date, cast, func

    end_date = datetime.now(UTC)
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
    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start.replace(day=1)

    # Consolidated counts (1 query replaces 6)
    ns_row = (
        await db.execute(
            select(
                func.count(NewsletterSubscriber.id).label("total"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.is_active)
                .label("active"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.is_confirmed)
                .label("confirmed"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.created_at >= today_start)
                .label("new_today"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.created_at >= week_start)
                .label("new_week"),
                func.count(NewsletterSubscriber.id)
                .filter(NewsletterSubscriber.created_at >= month_start)
                .label("new_month"),
            )
        )
    ).one()
    total = ns_row.total
    active = ns_row.active
    confirmed = ns_row.confirmed
    new_today = ns_row.new_today
    new_week = ns_row.new_week
    new_month = ns_row.new_month

    # By source
    sources_result = await db.execute(
        select(NewsletterSubscriber.source, func.count(NewsletterSubscriber.id)).group_by(
            NewsletterSubscriber.source
        )
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
    now = datetime.now(UTC)

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
    db_start = datetime.now(UTC)
    try:
        await db.execute(select(func.count(User.id)))
        db_response_time = (datetime.now(UTC) - db_start).total_seconds() * 1000
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
        "timestamp": datetime.now(UTC).isoformat(),
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
