from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, UserRole, Booking, BookingStatus, Vendor

router = APIRouter()


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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Total users
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0
    
    # Total vendors
    vendors_result = await db.execute(select(func.count(Vendor.id)))
    total_vendors = vendors_result.scalar() or 0
    
    # Total bookings
    bookings_result = await db.execute(select(func.count(Booking.id)))
    total_bookings = bookings_result.scalar() or 0
    
    # Revenue calculations
    revenue_result = await db.execute(
        select(func.coalesce(func.sum(Booking.total_amount), 0))
    )
    total_revenue = float(revenue_result.scalar() or 0)
    
    # Net revenue (after 10% commission)
    net_revenue = total_revenue * 0.90
    
    # Booking status counts
    pending_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.status == BookingStatus.PENDING)
    )
    pending_bookings = pending_result.scalar() or 0
    
    completed_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.status == BookingStatus.CONFIRMED)
    )
    completed_bookings = completed_result.scalar() or 0
    
    cancelled_result = await db.execute(
        select(func.count(Booking.id)).where(Booking.status == BookingStatus.CANCELLED)
    )
    cancelled_bookings = cancelled_result.scalar() or 0
    
    return OverviewStats(
        total_users=total_users,
        total_vendors=total_vendors,
        total_bookings=total_bookings,
        total_revenue=round(total_revenue, 2),
        net_revenue=round(net_revenue, 2),
        pending_bookings=pending_bookings,
        completed_bookings=completed_bookings,
        cancelled_bookings=cancelled_bookings
    )


@router.get("/revenue", response_model=list[RevenueData])
async def get_revenue_stats(
    period: str = Query("30", description="Days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    days = int(period)
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    results = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        day_start = date.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        
        # Get bookings for this day
        result = await db.execute(
            select(
                func.coalesce(func.sum(Booking.total_amount), 0).label("revenue"),
                func.count(Booking.id).label("count")
            ).where(
                and_(
                    Booking.created_at >= day_start,
                    Booking.created_at < day_end,
                    Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
                )
            )
        )
        row = result.one()
        
        gross = float(row.revenue or 0)
        results.append(RevenueData(
            date=date_str,
            gross_revenue=round(gross, 2),
            net_revenue=round(gross * 0.90, 2),
            bookings_count=row.count or 0
        ))
    
    return results


@router.get("/bookings/by-status", response_model=list[BookingStatusData])
async def get_bookings_by_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    results = []
    for status in BookingStatus:
        result = await db.execute(
            select(
                func.count(Booking.id).label("count"),
                func.coalesce(func.sum(Booking.total_amount), 0).label("revenue")
            ).where(Booking.status == status)
        )
        row = result.one()
        results.append(BookingStatusData(
            status=status.value,
            count=row.count or 0,
            revenue=float(row.revenue or 0)
        ))
    
    return results


@router.get("/top-vendors", response_model=list[TopVendorData])
async def get_top_vendors(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.execute(
        select(
            Vendor.id,
            Vendor.business_name,
            func.count(Booking.id).label("bookings"),
            func.coalesce(func.sum(Booking.total_amount), 0).label("revenue")
        ).join(Booking, Booking.vendor_id == Vendor.id)
        .group_by(Vendor.id, Vendor.business_name)
        .order_by(func.sum(Booking.total_amount).desc())
        .limit(limit)
    )
    
    return [
        TopVendorData(
            vendor_id=str(row.id),
            vendor_name=row.business_name,
            total_bookings=row.bookings,
            total_revenue=float(row.revenue or 0)
        )
        for row in result.all()
    ]


@router.get("/users/stats", response_model=UserStatsData)
async def get_user_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total
    total_result = await db.execute(select(func.count(User.id)))
    total = total_result.scalar() or 0
    
    # New today
    new_today_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= today_start)
    )
    new_today = new_today_result.scalar() or 0
    
    # New this week
    new_week_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_start)
    )
    new_this_week = new_week_result.scalar() or 0
    
    # New this month
    new_month_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= month_start)
    )
    new_this_month = new_month_result.scalar() or 0
    
    # By role
    role_result = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    by_role = {row[0].value: row[1] for row in role_result.all()}
    
    return UserStatsData(
        total=total,
        new_today=new_today,
        new_this_week=new_this_week,
        new_this_month=new_this_month,
        by_role=by_role
    )


@router.get("/traffic")
async def get_traffic_stats(
    period: str = Query("30", description="Days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Mock traffic data - in production, integrate with analytics service
    days = int(period)
    results = []
    
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=days - i - 1)
        date_str = date.strftime("%Y-%m-%d")
        
        # Simulate traffic - replace with real analytics
        import random
        results.append(TrafficData(
            date=date_str,
            pageviews=random.randint(500, 2000),
            unique_visitors=random.randint(200, 800)
        ))
    
    return {
        "data": results,
        "summary": {
            "total_pageviews": sum(r.pageviews for r in results),
            "total_visitors": sum(r.unique_visitors for r in results),
            "avg_daily_pageviews": sum(r.pageviews for r in results) // days,
            "avg_daily_visitors": sum(r.unique_visitors for r in results) // days
        }
    }


@router.get("/bookings/trends")
async def get_booking_trends(
    period: str = Query("30", description="Days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    days = int(period)
    results = []
    
    for i in range(days):
        date = datetime.now(timezone.utc) - timedelta(days=days - i - 1)
        date_str = date.strftime("%Y-%m-%d")
        
        day_start = date.replace(hour=0, minute=0, second=0)
        day_end = day_start + timedelta(days=1)
        
        result = await db.execute(
            select(func.count(Booking.id)).where(
                and_(
                    Booking.created_at >= day_start,
                    Booking.created_at < day_end
                )
            )
        )
        count = result.scalar() or 0
        
        results.append({
            "date": date_str,
            "bookings": count
        })
    
    return results