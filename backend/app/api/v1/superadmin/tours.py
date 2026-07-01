from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.core.utils import escape_like_pattern
from app.models import Tour, User, Vendor
from app.schemas import TourCreate, TourListResponse, TourResponse, TourUpdate

router = APIRouter(prefix="/tours", tags=["Super Admin - Tours"])


class SuperAdminTourCreate(TourCreate):
    vendor_id: UUID


@router.get("", response_model=dict)
async def list_tours(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    difficulty: str | None = Query(None),
    is_active: bool | None = Query(None),
    is_featured: bool | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(Tour.id))
    query = select(Tour)

    if search:
        safe = escape_like_pattern(search)
        like = f"%{safe}%"
        query = query.where((Tour.name.ilike(like)) | (Tour.location.ilike(like)))
        count_query = count_query.where((Tour.name.ilike(like)) | (Tour.location.ilike(like)))

    if category:
        query = query.where(Tour.category == category)
        count_query = count_query.where(Tour.category == category)

    if difficulty:
        query = query.where(Tour.difficulty == difficulty)
        count_query = count_query.where(Tour.difficulty == difficulty)

    if is_active is not None:
        query = query.where(Tour.is_active == is_active)
        count_query = count_query.where(Tour.is_active == is_active)

    if is_featured is not None:
        query = query.where(Tour.is_featured == is_featured)
        count_query = count_query.where(Tour.is_featured == is_featured)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    sort_col = getattr(Tour, sort_by, Tour.created_at)
    order_fn = desc if sort_order == "desc" else lambda c: c
    query = query.order_by(order_fn(sort_col))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    tours = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [TourListResponse.model_validate(t).model_dump() for t in tours],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{tour_id}", response_model=TourResponse)
async def get_tour(
    tour_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")
    return TourResponse.model_validate(tour)


@router.post("", response_model=TourResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_tour(
    request: Request,
    data: SuperAdminTourCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    import uuid as _uuid

    vendor_id = data.vendor_id

    v_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    if not v_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vendor not found")

    base_slug = data.name.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(_uuid.uuid4())[:8]}"

    tour = Tour(
        vendor_id=vendor_id,
        name=data.name,
        slug=slug,
        description=data.description,
        category=data.category,
        location=data.location,
        difficulty=data.difficulty,
        duration_hours=data.duration_hours,
        meeting_point=data.meeting_point,
        max_group_size=data.max_group_size,
        price=data.price,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(tour)
    await db.commit()
    await db.refresh(tour)
    return TourResponse.model_validate(tour)


@router.put("/{tour_id}", response_model=TourResponse)
@limiter.limit("10/minute")
async def update_tour(
    request: Request,
    tour_id: UUID,
    data: TourUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    update_data = data.model_dump(exclude_unset=True)
    allowed_fields = {
        "name",
        "description",
        "category",
        "difficulty",
        "location",
        "duration_hours",
        "duration_text",
        "meeting_point",
        "max_group_size",
        "min_age",
        "price",
        "currency",
        "included",
        "not_included",
        "itinerary",
        "images",
        "cover_image",
        "schedule_days",
        "is_featured",
        "is_active",
    }
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(tour, key, value)

    tour.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(tour)
    return TourResponse.model_validate(tour)


@router.delete("/{tour_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_tour(
    request: Request,
    tour_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    await db.delete(tour)
    await db.commit()
    return {"success": True, "message": "Tour deleted successfully"}


@router.post("/{tour_id}/feature", response_model=dict)
@limiter.limit("10/minute")
async def toggle_tour_featured(
    request: Request,
    tour_id: UUID,
    featured: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    tour.is_featured = featured
    tour.updated_at = datetime.now(UTC)
    await db.commit()
    return {
        "success": True,
        "is_featured": tour.is_featured,
        "message": f"Tour {'featured' if featured else 'unfeatured'} successfully",
    }
