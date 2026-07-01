import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import paginate_flat
from app.core.rate_limiter import limiter
from app.core.security import require_permission
from app.core.utils import escape_like_pattern
from app.models import User, UserRole, Vendor, Tour
from app.models.tour import TourCategory, TourDifficulty
from app.schemas import (
    TourResponse,
    TourCreate,
    TourUpdate,
    TourListResponse,
    PaginationParams,
    PaginatedResponse,
)
from app.services.cache_service import cache
from app.services.cloudinary_service import cloudinary_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Tours"])

CACHE_TTL_LIST = 300  # 5 minutes for tour lists
CACHE_TTL_DETAIL = 600  # 10 minutes for tour details
CACHE_TTL_FEATURED = 180  # 3 minutes for featured tours


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List tours",
    description="Paginated list of active tours with optional filters by category, difficulty, location, price range, rating, featured status, duration, text search, and sorting.",
)
async def get_tours(
    params: PaginationParams = Depends(),
    category: str = None,
    difficulty: str = None,
    location: str = None,
    destination: str = None,
    min_price: float = None,
    max_price: float = None,
    rating: float = None,
    min_rating: float = None,
    featured: bool = None,
    q: str = None,
    min_duration: float = None,
    max_duration: float = None,
    sort: str = None,
    db: AsyncSession = Depends(get_db),
):
    use_rating = rating if rating is not None else min_rating
    use_location = location or destination

    # Generate cache key based on query parameters
    cache_key = (
        f"tours:list:{category}:{difficulty}:{use_location}:"
        f"{min_price}:{max_price}:{use_rating}:{featured}:"
        f"{q}:{min_duration}:{max_duration}:{sort}:"
        f"{params.page}:{params.page_size}"
    )

    # Try to get from cache
    cached = await cache.get(cache_key)
    if cached:
        return PaginatedResponse(**cached)

    # Build query with eager loading
    query = select(Tour).where(Tour.is_active)
    query = query.options(selectinload(Tour.vendor))

    if category:
        query = query.where(Tour.category == TourCategory(category))
    if difficulty:
        query = query.where(Tour.difficulty == TourDifficulty(difficulty))
    if use_location:
        pattern = f"%{escape_like_pattern(use_location)}%"
        query = query.where(Tour.location.ilike(pattern))
    if min_price is not None:
        query = query.where(Tour.price >= min_price)
    if max_price is not None:
        query = query.where(Tour.price <= max_price)
    if use_rating is not None:
        query = query.where(Tour.rating >= use_rating)
    if featured:
        query = query.where(Tour.is_featured)
    if q:
        pattern = f"%{escape_like_pattern(q)}%"
        query = query.where(Tour.name.ilike(pattern) | Tour.description.ilike(pattern))
    if min_duration is not None:
        query = query.where(Tour.duration_hours >= min_duration)
    if max_duration is not None:
        query = query.where(Tour.duration_hours <= max_duration)

    # Map sort parameter to order_by
    sort_map = {
        "popular": Tour.rating.desc().nullslast(),
        "price_asc": Tour.price.asc(),
        "price_desc": Tour.price.desc(),
        "rating": Tour.rating.desc().nullslast(),
        "newest": Tour.created_at.desc(),
    }
    order = sort_map.get(sort, Tour.created_at.desc())

    response = await paginate_flat(
        db,
        query,
        params,
        transform_func=TourListResponse.model_validate,
        order_by=order,
    )

    # Cache the response
    ttl = CACHE_TTL_FEATURED if featured else CACHE_TTL_LIST
    await cache.set(cache_key, response.model_dump(), ttl=ttl, tags=["tours"])

    return response


@router.get(
    "/{tour_id}",
    response_model=TourResponse,
    summary="Get tour by ID",
    description="Returns a single tour with vendor details by its UUID.",
)
async def get_tour(tour_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cache_key = f"tours:detail:{tour_id}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return TourResponse(**cached)

    # Query with eager loading
    result = await db.execute(
        select(Tour).where(Tour.id == tour_id).options(selectinload(Tour.vendor))
    )
    tour = result.scalar_one_or_none()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found"
        )

    response = TourResponse.model_validate(tour)
    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["tours", f"tour:{tour_id}"],
    )

    return response


@router.get(
    "/slug/{slug}",
    response_model=TourResponse,
    summary="Get tour by slug",
    description="Returns a single tour by its URL-friendly slug.",
)
async def get_tour_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"tours:slug:{slug}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return TourResponse(**cached)

    # Query with eager loading
    result = await db.execute(
        select(Tour).where(Tour.slug == slug).options(selectinload(Tour.vendor))
    )
    tour = result.scalar_one_or_none()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found"
        )

    response = TourResponse.model_validate(tour)
    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["tours", f"tour:{tour.id}"],
    )

    return response


@router.post(
    "",
    response_model=TourResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tour",
    description="Creates a new tour listing. Vendor or SUPER_ADMIN role required.",
)
@limiter.limit("10/minute")
async def create_tour(
    request: Request,
    data: TourCreate,
    current_user: User = Depends(require_permission("tours", "create")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found"
        )

    # Generate slug
    base_slug = data.name.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {
        "name",
        "description",
        "category",
        "location",
        "duration_hours",
        "difficulty",
        "meeting_point",
        "max_group_size",
        "price",
        "currency",
        "duration_text",
        "min_age",
        "included",
        "not_included",
        "itinerary",
        "images",
        "cover_image",
        "schedule_days",
        "is_active",
        "is_featured",
    }
    tour_data_filtered = {
        k: v for k, v in data.model_dump().items() if k in allowed_fields
    }

    tour = Tour(vendor_id=vendor.id, slug=slug, **tour_data_filtered)
    db.add(tour)
    await db.flush()
    await db.commit()

    # Invalidate tours list cache
    await cache.invalidate_tag("tours")

    return TourResponse.model_validate(tour)


@router.put(
    "/{tour_id}",
    response_model=TourResponse,
    summary="Update tour",
    description="Updates a tour. Only the owning vendor or SUPER_ADMIN can update.",
)
@limiter.limit("10/minute")
async def update_tour(
    request: Request,
    tour_id: uuid.UUID,
    data: TourUpdate,
    current_user: User = Depends(require_permission("tours", "update")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found"
        )

    # Ownership check: vendor solo puede editar sus propios tours
    if current_user.role == UserRole.VENDOR:
        result_vendor = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = result_vendor.scalar_one_or_none()
        if not vendor or tour.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this tour",
            )

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {
        "name",
        "description",
        "category",
        "location",
        "duration_hours",
        "difficulty",
        "meeting_point",
        "max_group_size",
        "price",
        "currency",
        "duration_text",
        "min_age",
        "included",
        "not_included",
        "itinerary",
        "images",
        "cover_image",
        "schedule_days",
        "is_active",
        "is_featured",
    }

    for field, value in data.model_dump(exclude_unset=True).items():
        if field in allowed_fields:
            setattr(tour, field, value)

    await db.flush()
    await db.commit()

    # Invalidate caches
    await cache.invalidate_tag("tours")
    await cache.invalidate_tag(f"tour:{tour_id}")
    await cache.delete(f"tours:detail:{tour_id}")
    await cache.delete(f"tours:slug:{tour.slug}")

    return TourResponse.model_validate(tour)


@router.delete(
    "/{tour_id}",
    response_model=dict,
    summary="Delete tour (soft)",
    description="Soft-deletes a tour by setting is_active=False. Only the owning vendor or SUPER_ADMIN.",
)
async def delete_tour(
    tour_id: uuid.UUID,
    current_user: User = Depends(require_permission("tours", "delete")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()

    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tour not found"
        )

    # Ownership check
    if current_user.role == UserRole.VENDOR:
        result_vendor = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = result_vendor.scalar_one_or_none()
        if not vendor or tour.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this tour",
            )

    tour.is_active = False
    await db.flush()
    await db.commit()

    # Invalidate caches
    await cache.invalidate_tag("tours")
    await cache.invalidate_tag(f"tour:{tour_id}")
    await cache.delete(f"tours:detail:{tour_id}")
    await cache.delete(f"tours:slug:{tour.slug}")

    return {"message": "Tour deleted successfully"}


@router.get(
    "/vendor/my",
    response_model=PaginatedResponse,
    summary="Get my tours (vendor)",
    description="Returns the authenticated vendor's own tours with pagination.",
)
async def get_my_tours(
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_permission("tours", "read")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource",
        )

    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        return PaginatedResponse(
            items=[],
            total=0,
            page=params.page,
            page_size=params.page_size,
            total_pages=0,
            has_next=False,
            has_prev=False,
        )

    query = select(Tour).where(Tour.vendor_id == vendor.id)

    response = await paginate_flat(
        db,
        query,
        params,
        transform_func=TourListResponse.model_validate,
        order_by=Tour.created_at.desc(),
    )

    return response


@router.get(
    "/categories",
    response_model=list[str],
    summary="List tour categories",
    description="Returns a distinct list of all categories from active tours.",
)
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tour.category).where(Tour.is_active).distinct())
    categories = [r[0] for r in result.all() if r[0]]
    return categories


@router.post(
    "/{tour_id}/gallery",
    response_model=dict,
    summary="Upload tour gallery images",
    description="Upload multiple images to the tour's gallery. Accepted formats: jpg, jpeg, png, gif, webp. Max 10MB each.",
)
@limiter.limit("5/minute")
async def upload_tour_gallery(
    request: Request,
    tour_id: uuid.UUID,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_permission("tours", "update")),
    db: AsyncSession = Depends(get_db),
):
    from app.services.cloudinary_service import CloudinaryError

    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour not found")

    if current_user.role == UserRole.VENDOR and tour.vendor_id:
        v_result = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = v_result.scalar_one_or_none()
        if not vendor or tour.vendor_id != vendor.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    current_images = list(tour.images or [])
    uploaded = []

    for file in files:
        if not file.filename:
            continue
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in {"jpg", "jpeg", "png", "gif", "webp"}:
            continue
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            continue

        try:
            upload_result = await cloudinary_service.upload_image(
                file_content=contents,
                folder="tours",
                filename=file.filename,
            )
            image_url = upload_result.get("secure_url") or upload_result.get("url")
            if image_url:
                current_images.append(image_url)
                uploaded.append(image_url)
        except CloudinaryError as e:
            logger.error(f"Failed to upload tour image: {e}")

    tour.images = current_images
    db.add(tour)
    await db.commit()

    return {"uploaded": uploaded, "total_images": len(current_images)}
