import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.schemas import (
    DestinationResponse, DestinationCreate, DestinationUpdate
)
from app.models import User, UserRole, Destination
from app.services.cache_service import cache

router = APIRouter()

CACHE_TTL_LIST = 600  # 10 minutes for destination lists
CACHE_TTL_DETAIL = 900  # 15 minutes for destination details (rarely change)


@router.get("", response_model=list[DestinationResponse])
async def get_destinations(
    db: AsyncSession = Depends(get_db),
    region: str = None,
    featured: bool = None
):
    cache_key = f"destinations:list:{region}:{featured}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return [DestinationResponse(**item) for item in cached]
    
    query = select(Destination).where(Destination.is_active)
    
    if region:
        query = query.where(Destination.region == region)
    if featured:
        query = query.where(Destination.is_featured)
    
    query = query.order_by(Destination.order.asc())
    result = await db.execute(query)
    destinations = result.scalars().all()
    
    response = [DestinationResponse.model_validate(d) for d in destinations]
    
    # Cache the response
    ttl = CACHE_TTL_LIST
    await cache.set(cache_key, [item.model_dump() for item in response], ttl=ttl, tags=["destinations"])
    
    return response


@router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(
    destination_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"destinations:detail:{destination_id}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return DestinationResponse(**cached)
    
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    response = DestinationResponse.model_validate(destination)
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["destinations", f"destination:{destination_id}"])
    
    return response


@router.get("/slug/{slug}", response_model=DestinationResponse)
async def get_destination_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"destinations:slug:{slug}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return DestinationResponse(**cached)
    
    result = await db.execute(select(Destination).where(Destination.slug == slug))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    response = DestinationResponse.model_validate(destination)
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["destinations", f"destination:{destination.id}"])
    
    return response


@router.post("", response_model=DestinationResponse)
async def create_destination(
    data: DestinationCreate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    slug = data.name.lower().replace(" ", "-")
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = ['name', 'description', 'region', 'country', 'highlights',
                     'best_time_to_visit', 'weather_info', 'getting_there', 
                     'local_tips', 'latitude', 'longitude', 'photos', 
                     'featured_photo', 'is_featured', 'order']
    destination_data_filtered = {k: v for k, v in data.model_dump().items() if k in allowed_fields}
    
    destination = Destination(
        slug=slug,
        **destination_data_filtered
    )
    db.add(destination)
    await db.flush()
    await db.commit()
    
    # Invalidate destinations cache
    await cache.invalidate_tag("destinations")
    
    return DestinationResponse.model_validate(destination)


@router.put("/{destination_id}", response_model=DestinationResponse)
async def update_destination(
    destination_id: uuid.UUID,
    data: DestinationUpdate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'name', 'description', 'region', 'country', 'highlights',
                     'best_time_to_visit', 'weather_info', 'getting_there',
                     'local_tips', 'latitude', 'longitude', 'photos',
                     'featured_photo', 'is_featured', 'order', 'is_active'}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in allowed_fields:
            setattr(destination, field, value)
    
    await db.flush()
    await db.commit()
    
    # Invalidate caches
    await cache.invalidate_tag("destinations")
    await cache.invalidate_tag(f"destination:{destination_id}")
    await cache.delete(f"destinations:detail:{destination_id}")
    await cache.delete(f"destinations:slug:{destination.slug}")
    
    return DestinationResponse.model_validate(destination)


@router.delete("/{destination_id}")
async def delete_destination(
    destination_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    destination.is_active = False
    await db.flush()
    await db.commit()
    
    # Invalidate caches
    await cache.invalidate_tag("destinations")
    await cache.invalidate_tag(f"destination:{destination_id}")
    await cache.delete(f"destinations:detail:{destination_id}")
    await cache.delete(f"destinations:slug:{destination.slug}")
    
    return {"message": "Destination deleted successfully"}


@router.put("/{destination_id}/order")
async def reorder_destination(
    destination_id: uuid.UUID,
    order: int,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    destination = result.scalar_one_or_none()
    
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    destination.order = order
    await db.flush()
    await db.commit()
    
    return {"message": "Destination order updated"}