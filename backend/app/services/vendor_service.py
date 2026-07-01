"""
Vendor service for shared business logic across public, admin, and superadmin routes.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Booking, Property, Review, Vendor
from app.services.cache_service import cache

CACHE_TTL_DETAIL = 600


class VendorService:
    """Shared vendor operations used across route layers."""

    @staticmethod
    async def get_or_404(db: AsyncSession, vendor_id: UUID) -> Vendor:
        result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = result.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
        return vendor

    @staticmethod
    async def get_with_user_or_404(db: AsyncSession, vendor_id: UUID) -> Vendor:
        result = await db.execute(
            select(Vendor).options(selectinload(Vendor.user)).where(Vendor.id == vendor_id)
        )
        vendor = result.scalar_one_or_none()
        if not vendor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
        return vendor

    @staticmethod
    async def invalidate_cache(vendor_id: UUID, slug: str | None = None):
        await cache.delete(f"vendors:detail:{vendor_id}")
        if slug:
            await cache.delete(f"vendors:slug:{slug}")
        await cache.invalidate_tag("vendors")

    @staticmethod
    async def calculate_stats(db: AsyncSession, vendor_id: UUID) -> dict:
        b_result = await db.execute(
            select(
                func.count(Booking.id).label("total"),
                func.sum(Booking.total_amount).label("revenue"),
                func.sum(case((Booking.status == "completed", 1), else_=0)).label("completed"),
                func.sum(case((Booking.status == "cancelled", 1), else_=0)).label("cancelled"),
            ).where(Booking.vendor_id == vendor_id)
        )
        b_row = b_result.one()

        prop_subq = select(Property.id).where(Property.vendor_id == vendor_id)
        tour_subq = select(Tour.id).where(Tour.vendor_id == vendor_id)
        r_result = await db.execute(
            select(
                func.avg(Review.rating).label("avg_rating"),
                func.count(Review.id).label("total_reviews"),
            ).where(
                or_(
                    Review.property_id.in_(prop_subq),
                    Review.tour_id.in_(tour_subq),
                )
            )
        )
        r_row = r_result.one()

        p_result = await db.execute(
            select(func.count(Property.id)).where(Property.vendor_id == vendor_id)
        )
        total_properties = p_result.scalar() or 0

        return {
            "vendor_id": vendor_id,
            "total_bookings": b_row.total or 0,
            "total_revenue": float(b_row.revenue or 0),
            "completed_bookings": b_row.completed or 0,
            "cancelled_bookings": b_row.cancelled or 0,
            "average_rating": float(r_row.avg_rating or 0),
            "total_reviews": r_row.total_reviews or 0,
            "total_properties": total_properties,
            "response_rate": 0.0,
            "avg_response_time_minutes": None,
        }

    @staticmethod
    async def run_compliance_check(db: AsyncSession, vendor: Vendor) -> list[str]:
        flags = []

        result = await db.execute(
            select(func.count(Property.id)).where(Property.vendor_id == vendor.id)
        )
        if (result.scalar() or 0) == 0:
            flags.append("no_properties")

        result = await db.execute(
            select(
                func.count().label("total"),
                func.sum(case((Booking.status == "completed", 1), else_=0)).label("completed"),
            ).where(Booking.vendor_id == vendor.id)
        )
        row = result.one()
        if row.total and row.total > 0:
            completion_rate = (row.completed or 0) / row.total
            if completion_rate < 0.5:
                flags.append("low_completion_rate")

        if vendor.rating and vendor.rating < 2.0:
            flags.append("low_rating")

        return flags
