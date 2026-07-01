from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Booking, BookingStatus, User, UserRole, Vendor

router = APIRouter(tags=["Analytics"])


# Analytics Response Models
class OverviewStats(BaseModel):
    total_users: int
    total_vendors: int
    total_bookings: int
    total_revenue: float
    net_revenue: float
    pending_bookings: int
    completed_bookings: int
    cancelled_bookings: int


class RevenueData(BaseModel):
    date: str
    gross_revenue: float
    net_revenue: float
    bookings_count: int


class BookingStatusData(BaseModel):
    status: str
    count: int
    revenue: float


class TopVendorData(BaseModel):
    vendor_id: str
    vendor_name: str
    total_bookings: int
    total_revenue: float


class TrafficData(BaseModel):
    date: str
    pageviews: int
    unique_visitors: int


class UserStatsData(BaseModel):
    total: int
    new_today: int
    new_this_week: int
    new_this_month: int
    by_role: dict


class DestinationStats(BaseModel):
    destination_name: str
    bookings_count: int
    revenue: float


@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Parallelizable queries (3 round-trips instead of 7)
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0

    vendors_result = await db.execute(select(func.count(Vendor.id)))
    total_vendors = vendors_result.scalar() or 0

    # Aggregated booking stats in a single query
    booking_stats = await db.execute(
        select(
            func.count(Booking.id).label("total"),
            func.coalesce(func.sum(Booking.total_amount), 0).label("total_revenue"),
            func.sum(case((Booking.status == BookingStatus.PENDING, 1), else_=0)).label("pending"),
            func.sum(case((Booking.status == BookingStatus.CONFIRMED, 1), else_=0)).label(
                "confirmed"
            ),
            func.sum(case((Booking.status == BookingStatus.CANCELLED, 1), else_=0)).label(
                "cancelled"
            ),
        )
    )
    stats = booking_stats.one()

    total_revenue = float(stats.total_revenue or 0)

    return OverviewStats(
        total_users=total_users,
        total_vendors=total_vendors,
        total_bookings=stats.total or 0,
        total_revenue=round(total_revenue, 2),
        net_revenue=round(total_revenue * 0.90, 2),
        pending_bookings=stats.pending or 0,
        completed_bookings=stats.confirmed or 0,
        cancelled_bookings=stats.cancelled or 0,
    )


@router.get("/revenue", response_model=list[RevenueData])
async def get_revenue_stats(
    period: str = Query("30", description="Days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    days = int(period)
    start_date = datetime.now(UTC) - timedelta(days=days)

    # Single aggregated query instead of per-day loop
    day_expr = func.date_trunc("day", Booking.created_at)
    result = await db.execute(
        select(
            day_expr.label("day"),
            func.coalesce(func.sum(Booking.total_amount), 0).label("revenue"),
            func.count(Booking.id).label("count"),
        )
        .where(
            and_(
                Booking.created_at >= start_date,
                Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
            )
        )
        .group_by(day_expr)
        .order_by(day_expr)
    )
    rows = {r.day.strftime("%Y-%m-%d"): r for r in result.all()}

    results = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        row = rows.get(date_str)

        gross = float(row.revenue) if row else 0
        results.append(
            RevenueData(
                date=date_str,
                gross_revenue=round(gross, 2),
                net_revenue=round(gross * 0.90, 2),
                bookings_count=row.count if row else 0,
            )
        )

    return results


@router.get("/bookings/by-status", response_model=list[BookingStatusData])
async def get_bookings_by_status(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Single aggregated query
    result = await db.execute(
        select(
            Booking.status,
            func.count(Booking.id).label("count"),
            func.coalesce(func.sum(Booking.total_amount), 0).label("revenue"),
        ).group_by(Booking.status)
    )
    row_map = {r.status: r for r in result.all()}

    return [
        BookingStatusData(
            status=s.value,
            count=row_map.get(s).count if row_map.get(s) else 0,
            revenue=float(row_map.get(s).revenue) if row_map.get(s) else 0,
        )
        for s in BookingStatus
    ]


@router.get("/top-vendors", response_model=list[TopVendorData])
async def get_top_vendors(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(
            Vendor.id,
            Vendor.business_name,
            func.count(Booking.id).label("bookings"),
            func.coalesce(func.sum(Booking.total_amount), 0).label("revenue"),
        )
        .join(Booking, Booking.vendor_id == Vendor.id)
        .group_by(Vendor.id, Vendor.business_name)
        .order_by(func.sum(Booking.total_amount).desc())
        .limit(limit)
    )

    return [
        TopVendorData(
            vendor_id=str(row.id),
            vendor_name=row.business_name,
            total_bookings=row.bookings,
            total_revenue=float(row.revenue or 0),
        )
        for row in result.all()
    ]


@router.get("/users/stats", response_model=UserStatsData)
async def get_user_stats(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    now = datetime.now(UTC)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Single aggregated query for user counts and role breakdown
    result = await db.execute(
        select(
            func.count(User.id).label("total"),
            func.sum(case((User.created_at >= today_start, 1), else_=0)).label("new_today"),
            func.sum(case((User.created_at >= week_start, 1), else_=0)).label("new_week"),
            func.sum(case((User.created_at >= month_start, 1), else_=0)).label("new_month"),
            User.role,
            func.count(User.id).label("role_count"),
        ).group_by(User.role)
    )
    rows = result.all()

    total = sum(r.total for r in rows) if rows else 0
    new_today = sum(r.new_today for r in rows) if rows else 0
    new_this_week = sum(r.new_week for r in rows) if rows else 0
    new_this_month = sum(r.new_month for r in rows) if rows else 0
    by_role = {r.role.value if hasattr(r.role, "value") else r.role: r.role_count for r in rows}

    return UserStatsData(
        total=total,
        new_today=new_today,
        new_this_week=new_this_week,
        new_this_month=new_this_month,
        by_role=by_role,
    )


@router.get("/traffic", response_model=dict)
async def get_traffic_stats(
    period: str = Query("30", description="Days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    # TODO: implement real analytics tracking (pageviews, unique visitors)
    days = int(period)
    results = []

    for i in range(days):
        date = datetime.now(UTC) - timedelta(days=days - i - 1)
        date_str = date.strftime("%Y-%m-%d")

        results.append(TrafficData(date=date_str, pageviews=0, unique_visitors=0))

    return {
        "data": results,
        "summary": {
            "total_pageviews": sum(r.pageviews for r in results),
            "total_visitors": sum(r.unique_visitors for r in results),
            "avg_daily_pageviews": sum(r.pageviews for r in results) // days,
            "avg_daily_visitors": sum(r.unique_visitors for r in results) // days,
        },
    }


@router.get("/bookings/trends", response_model=dict)
async def get_booking_trends(
    period: str = Query("30", description="Days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    days = int(period)
    start_date = datetime.now(UTC) - timedelta(days=days)

    # Single aggregated query
    day_expr = func.date_trunc("day", Booking.created_at)
    result = await db.execute(
        select(
            day_expr.label("day"),
            func.count(Booking.id).label("count"),
        )
        .where(Booking.created_at >= start_date)
        .group_by(day_expr)
        .order_by(day_expr)
    )
    counts = {r.day.strftime("%Y-%m-%d"): r.count for r in result.all()}

    return [
        {
            "date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "bookings": counts.get((start_date + timedelta(days=i)).strftime("%Y-%m-%d"), 0),
        }
        for i in range(days)
    ]
