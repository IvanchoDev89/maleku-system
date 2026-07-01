"""
Super Admin Reviews Management endpoints.
Moderation of reviews and ratings.
"""

from datetime import UTC
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.pagination import paginate_flat
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.models import Review, User
from app.schemas import PaginatedResponse, PaginationParams

router = APIRouter(tags=["SuperAdmin - Reviews"])


class ReviewListItem(BaseModel):
    """Review item for list view."""

    id: str
    user_id: str
    user_name: str
    user_email: str
    property_id: str | None = None
    property_name: str | None = None
    tour_id: str | None = None
    tour_name: str | None = None
    booking_id: str | None = None
    rating: int
    title: str | None = None
    comment: str | None = None
    is_approved: bool
    created_at: str


class ReviewUpdateRequest(BaseModel):
    """Request to update review moderation status."""

    is_approved: bool


def review_to_item(review: Review, user: User | None = None) -> ReviewListItem:
    """Convert a Review model to a ReviewListItem."""
    return ReviewListItem(
        id=str(review.id),
        user_id=str(review.user_id),
        user_name=user.full_name if user else "Unknown",
        user_email=user.email if user else "unknown@email.com",
        property_id=str(review.property_id) if review.property_id else None,
        property_name=review.property.name if review.property else None,
        tour_id=str(review.tour_id) if review.tour_id else None,
        tour_name=review.tour.name if review.tour else None,
        booking_id=str(review.booking_id) if review.booking_id else None,
        rating=review.rating,
        title=review.title,
        comment=review.comment,
        is_approved=review.is_approved,
        created_at=review.created_at.isoformat() if review.created_at else "",
    )


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List all reviews (superadmin)",
    description="Returns all reviews with user and service info. Supports filters.",
)
async def list_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_superadmin()),
):
    query = (
        select(Review)
        .where(Review.deleted_at.is_(None))
        .options(
            selectinload(Review.user),
            selectinload(Review.property),
            selectinload(Review.tour),
        )
    )

    if status_filter == "approved":
        query = query.where(Review.is_approved == True)
    elif status_filter == "pending":
        query = query.where(Review.is_approved == False)

    params = PaginationParams(page=page, page_size=page_size)
    result = await paginate_flat(
        db,
        query,
        params,
        order_by=desc(Review.created_at),
    )

    items = []
    for review in result.items:
        items.append(review_to_item(review, review.user).model_dump())

    result.items = items
    return result


@router.put(
    "/{review_id}",
    response_model=dict,
    summary="Update review moderation",
    description="Approve or reject a review.",
)
@limiter.limit("10/minute")
async def update_review(
    request: Request,
    review_id: UUID,
    body: ReviewUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.is_approved = body.is_approved
    await db.commit()
    return {"success": True, "is_approved": review.is_approved}


@router.delete(
    "/{review_id}",
    response_model=dict,
    summary="Soft delete review",
    description="Soft-deletes a review.",
)
async def delete_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_superadmin()),
):
    from datetime import datetime

    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.deleted_at = datetime.now(UTC)
    await db.commit()
    return {"success": True}
