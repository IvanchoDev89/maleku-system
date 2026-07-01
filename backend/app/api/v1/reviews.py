from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Booking, BookingStatus, Property, Review, Tour, User, Vendor

router = APIRouter(tags=["Reviews"])


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    booking_id: UUID
    rating: int = Field(..., ge=1, le=5)
    title: str | None = None
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    user_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.post("/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Booking).where(
            Booking.id == data.booking_id,
            Booking.user_id == current_user.id,
        )
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or does not belong to you",
        )

    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only review completed bookings",
        )

    existing = await db.execute(select(Review).where(Review.booking_id == data.booking_id))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this booking",
        )

    if not booking.property_id and not booking.tour_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This booking has no associated service to review",
        )

    review = Review(
        user_id=current_user.id,
        booking_id=booking.id,
        property_id=booking.property_id,
        tour_id=booking.tour_id,
        rating=data.rating,
        title=data.title,
        comment=data.comment,
        is_approved=True,
    )
    db.add(review)
    await db.flush()

    vendor_id = booking.vendor_id
    if vendor_id:
        prop_subq = select(Property.id).where(Property.vendor_id == vendor_id)
        tour_subq = select(Tour.id).where(Tour.vendor_id == vendor_id)
        stats = await db.execute(
            select(
                func.avg(Review.rating).label("avg"),
                func.count(Review.id).label("cnt"),
            ).where(
                Review.is_approved == True,
                Review.deleted_at == None,
                or_(
                    Review.property_id.in_(prop_subq),
                    Review.tour_id.in_(tour_subq),
                ),
            )
        )
        row = stats.one()
        await db.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
        vendor = vendor_result.scalar_one_or_none()
        if vendor:
            vendor.rating = round(float(row.avg or 0), 1)
            vendor.total_reviews = row.cnt or 0

    await db.commit()
    await db.refresh(review, relationship="user")

    return ReviewResponse(
        id=review.id,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        user_name=current_user.full_name,
        created_at=review.created_at,
    )
