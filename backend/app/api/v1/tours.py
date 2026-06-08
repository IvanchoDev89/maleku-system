import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.pagination import paginate_flat
from app.core.security import get_current_user
from app.core.utils import escape_like_pattern
from app.models import User, UserRole, Vendor, Tour
from app.schemas import (
    TourResponse, TourCreate, TourUpdate,
    TourListResponse, PaginationParams, PaginatedResponse
)
from app.services.cache_service import cache

router = APIRouter(tags=["Tours"])

CACHE_TTL_LIST = 300  # 5 minutes for tour lists
CACHE_TTL_DETAIL = 600  # 10 minutes for tour details
CACHE_TTL_FEATURED = 180  # 3 minutes for featured tours


@router.get("", response_model=PaginatedResponse,
            summary="List tours",
            description="Paginated list of active tours with optional filters by category, difficulty, location, price range, rating, and featured status.")
async def get_tours(
    params: PaginationParams = Depends(),
    category: str = None,
    difficulty: str = None,
    location: str = None,
    min_price: float = None,
    max_price: float = None,
    rating: float = None,
    featured: bool = None,
    db: AsyncSession = Depends(get_db)
):
    # Generate cache key based on query parameters
    cache_key = f"tours:list:{category}:{difficulty}:{location}:{min_price}:{max_price}:{rating}:{featured}:{params.page}:{params.page_size}"
    
    # Try to get from cache
    cached = await cache.get(cache_key)
    if cached:
        return PaginatedResponse(**cached)
    
    # Build query with eager loading
    query = select(Tour).where(Tour.is_active)
    query = query.options(selectinload(Tour.vendor))
    
    if category:
        query = query.where(Tour.category == category)
    if difficulty:
        query = query.where(Tour.difficulty == difficulty)
    if location:
        query = query.where(Tour.location.ilike(f"%{escape_like_pattern(location)}%"))
    if rating:
        query = query.where(Tour.rating >= rating)
    if featured:
        query = query.where(Tour.is_featured)
    
    response = await paginate_flat(
        db, query, params,
        transform_func=TourListResponse.model_validate,
        order_by=Tour.created_at.desc()
    )
    
    # Cache the response
    ttl = CACHE_TTL_FEATURED if featured else CACHE_TTL_LIST
    await cache.set(cache_key, response, ttl=ttl, tags=["tours"])
    
    return PaginatedResponse(**response)


@router.get("/{tour_id}", response_model=TourResponse,
            summary="Get tour by ID",
            description="Returns a single tour with vendor details by its UUID.")
async def get_tour(
    tour_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    response = TourResponse.model_validate(tour)
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["tours", f"tour:{tour_id}"])
    
    return response


@router.get("/slug/{slug}", response_model=TourResponse,
            summary="Get tour by slug",
            description="Returns a single tour by its URL-friendly slug.")
async def get_tour_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    response = TourResponse.model_validate(tour)
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["tours", f"tour:{tour.id}"])
    
    return response


@router.post("", response_model=TourResponse,
             summary="Create tour",
             description="Creates a new tour listing. Vendor or SUPER_ADMIN role required.")
async def create_tour(
    data: TourCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can create tours"
        )
    
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Generate slug
    base_slug = data.name.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = ['name', 'description', 'short_description', 'tour_type', 'location',
                     'duration_hours', 'difficulty', 'meeting_point', 'max_participants',
                     'min_participants', 'price', 'currency', 'included_items', 'excluded_items',
                     'important_notes', 'what_to_bring', 'photos', 'featured_photo', 'video_url',
                     'is_published', 'is_featured']
    tour_data_filtered = {k: v for k, v in data.model_dump().items() if k in allowed_fields}
    
    tour = Tour(
        vendor_id=vendor.id,
        slug=slug,
        **tour_data_filtered
    )
    db.add(tour)
    await db.flush()
    await db.commit()
    
    # Invalidate tours list cache
    await cache.invalidate_tag("tours")
    
    return TourResponse.model_validate(tour)


@router.put("/{tour_id}", response_model=TourResponse,
            summary="Update tour",
            description="Updates a tour. Only the owning vendor or SUPER_ADMIN can update.")
async def update_tour(
    tour_id: uuid.UUID,
    data: TourUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    
    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    # Check ownership
    result_vendor = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result_vendor.scalar_one_or_none()

    if not vendor and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor profile required to update tours"
        )

    if current_user.role != UserRole.SUPER_ADMIN and tour.vendor_id != vendor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this tour"
        )
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'name', 'description', 'short_description', 'tour_type', 'location',
                     'duration_hours', 'difficulty', 'meeting_point', 'max_participants',
                     'min_participants', 'price', 'currency', 'included_items', 'excluded_items',
                     'important_notes', 'what_to_bring', 'photos', 'featured_photo', 'video_url',
                     'is_published', 'is_featured'}
    
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


@router.delete("/{tour_id}",
               summary="Delete tour (soft)",
               description="Soft-deletes a tour by setting is_active=False. Only the owning vendor or SUPER_ADMIN.")
async def delete_tour(
    tour_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = result.scalar_one_or_none()
    
    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    result_vendor = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result_vendor.scalar_one_or_none()

    if not vendor and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor profile required to delete tours"
        )

    if current_user.role != UserRole.SUPER_ADMIN and tour.vendor_id != vendor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this tour"
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


@router.get("/vendor/my", response_model=PaginatedResponse,
            summary="Get my tours (vendor)",
            description="Returns the authenticated vendor's own tours with pagination.")
async def get_my_tours(
    params: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource"
        )
    
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        return PaginatedResponse(
            items=[], total=0, page=params.page, page_size=params.page_size,
            total_pages=0, has_next=False, has_prev=False
        )
    
    query = select(Tour).where(Tour.vendor_id == vendor.id)
    
    response = await paginate_flat(
        db, query, params,
        transform_func=TourListResponse.model_validate,
        order_by=Tour.created_at.desc()
    )
    
    return PaginatedResponse(**response)


@router.get("/categories",
            summary="List tour categories",
            description="Returns a distinct list of all categories from active tours.")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tour.category)
        .where(Tour.is_active)
        .distinct()
    )
    categories = [r[0] for r in result.all() if r[0]]
    return {"categories": categories}