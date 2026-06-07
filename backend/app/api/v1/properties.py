import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, UserRole, Vendor, Property
from app.schemas import (
    PropertyResponse, PropertyCreate, PropertyUpdate,
    PropertyListResponse, PaginationParams, PaginatedResponse
)
from app.services.cache_service import cache

router = APIRouter()

CACHE_TTL_LIST = 300  # 5 minutes for property lists
CACHE_TTL_DETAIL = 600  # 10 minutes for property details
CACHE_TTL_FEATURED = 180  # 3 minutes for featured properties


@router.get("", response_model=PaginatedResponse)
async def get_properties(
    params: PaginationParams = Depends(),
    region: str = None,
    property_type: str = None,
    min_price: float = None,
    max_price: float = None,
    rating: float = None,
    featured: bool = None,
    db: AsyncSession = Depends(get_db)
):
    # Generate cache key based on query parameters
    cache_key = f"properties:list:{region}:{property_type}:{min_price}:{max_price}:{rating}:{featured}:{params.page}:{params.page_size}"
    
    # Try to get from cache
    cached = await cache.get(cache_key)
    if cached:
        return PaginatedResponse(**cached)
    
    # Build query with eager loading
    query = select(Property).where(Property.is_active)
    query = query.options(selectinload(Property.rooms))
    
    if region:
        query = query.where(Property.region == region)
    if property_type:
        query = query.where(Property.property_type == property_type)
    if rating:
        query = query.where(Property.rating >= rating)
    if featured:
        query = query.where(Property.is_featured)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Get with pagination
    offset = (params.page - 1) * params.page_size
    query = query.order_by(Property.created_at.desc()).offset(offset).limit(params.page_size)
    result = await db.execute(query)
    properties = result.scalars().all()
    
    response = PaginatedResponse(
        items=[PropertyListResponse.model_validate(p) for p in properties],
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total,
        has_prev=params.page > 1
    )
    
    # Cache the response
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_LIST, tags=["properties"])
    
    return response


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    # Try to get from cache
    cache_key = f"properties:detail:{property_id}"
    cached = await cache.get(cache_key)
    if cached:
        return PropertyResponse(**cached)
    
    # Query with eager loading for all relationships
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.rooms),
            selectinload(Property.vendor),
            selectinload(Property.reviews)
        )
        .where(Property.id == property_id)
    )
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    return PropertyResponse.model_validate(property_obj)


@router.get("/slug/{slug}", response_model=PropertyResponse)
async def get_property_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    # Try to get from cache
    cache_key = f"properties:slug:{slug}"
    cached = await cache.get(cache_key)
    if cached:
        return PropertyResponse(**cached)
    
    # Query with eager loading
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.rooms),
            selectinload(Property.vendor),
            selectinload(Property.reviews)
        )
        .where(Property.slug == slug)
    )
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    response = PropertyResponse.model_validate(property_obj)
    
    # Cache the response
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["properties"])
    
    return response


@router.post("", response_model=PropertyResponse)
async def create_property(
    data: PropertyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can create properties"
        )
    
    # Get vendor
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
    allowed_fields = ['name', 'description', 'short_description', 'property_type', 'address',
                     'city', 'region', 'country', 'latitude', 'longitude', 'max_guests',
                     'bedrooms', 'bathrooms', 'amenities', 'house_rules', 'check_in_time',
                     'check_out_time', 'cancellation_policy', 'price_per_night', 'currency',
                     'min_nights', 'max_nights', 'photos', 'featured_photo', 'video_url',
                     'is_published', 'is_featured']
    property_data_filtered = {k: v for k, v in data.model_dump().items() if k in allowed_fields}
    
    property_obj = Property(
        vendor_id=vendor.id,
        slug=slug,
        **property_data_filtered
    )
    db.add(property_obj)
    await db.flush()
    await db.commit()
    
    # Invalidate property list cache
    await cache.invalidate_tag("properties")
    
    return PropertyResponse.model_validate(property_obj)


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: uuid.UUID,
    data: PropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check ownership
    result_vendor = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result_vendor.scalar_one_or_none()

    if not vendor and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor profile required to update properties"
        )

    if current_user.role != UserRole.SUPER_ADMIN and property_obj.vendor_id != vendor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this property"
        )
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'name', 'description', 'short_description', 'property_type', 'address',
                     'city', 'region', 'country', 'latitude', 'longitude', 'max_guests',
                     'bedrooms', 'bathrooms', 'amenities', 'house_rules', 'check_in_time',
                     'check_out_time', 'cancellation_policy', 'price_per_night', 'currency',
                     'min_nights', 'max_nights', 'photos', 'featured_photo', 'video_url',
                     'is_published', 'is_featured'}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in allowed_fields:
            setattr(property_obj, field, value)
    
    await db.flush()
    await db.commit()
    
    # Invalidate cache for this property and lists
    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")
    
    # Cache updated property
    response = PropertyResponse.model_validate(property_obj)
    await cache.set(f"properties:detail:{property_id}", response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["properties"])
    await cache.set(f"properties:slug:{property_obj.slug}", response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["properties"])
    
    return response


@router.delete("/{property_id}")
async def delete_property(
    property_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check ownership
    result_vendor = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result_vendor.scalar_one_or_none()

    if not vendor and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor profile required to delete properties"
        )

    if current_user.role != UserRole.SUPER_ADMIN and property_obj.vendor_id != vendor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this property"
        )
    
    property_obj.is_active = False
    await db.flush()
    await db.commit()
    
    # Invalidate cache for this property and lists
    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")
    
    return {"message": "Property deleted successfully"}


@router.get("/vendor/my", response_model=PaginatedResponse)
async def get_my_properties(
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
    
    query = select(Property).where(Property.vendor_id == vendor.id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    offset = (params.page - 1) * params.page_size
    query = query.options(selectinload(Property.rooms)).order_by(Property.created_at.desc()).offset(offset).limit(params.page_size)
    result = await db.execute(query)
    properties = result.scalars().all()
    
    return PaginatedResponse(
        items=[PropertyListResponse.model_validate(p) for p in properties],
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=(total + params.page_size - 1) // params.page_size,
        has_next=params.page * params.page_size < total,
        has_prev=params.page > 1
    )


@router.get("/regions")
async def get_regions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Property.region)
        .where(Property.is_active)
        .distinct()
    )
    regions = [r[0] for r in result.all() if r[0]]
    return {"regions": regions}