from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.core.utils import escape_like_pattern
from app.models import Destination, User
from app.schemas import DestinationCreate, DestinationResponse, DestinationUpdate

router = APIRouter(prefix="/destinations", tags=["Super Admin - Destinations"])


@router.get("", response_model=dict)
async def list_destinations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    region: str | None = Query(None),
    is_active: bool | None = Query(None),
    is_featured: bool | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(Destination.id))
    query = select(Destination)

    if search:
        safe = escape_like_pattern(search)
        like = f"%{safe}%"
        query = query.where((Destination.name.ilike(like)) | (Destination.region.ilike(like)))
        count_query = count_query.where(
            (Destination.name.ilike(like)) | (Destination.region.ilike(like))
        )

    if region:
        query = query.where(Destination.region == region)
        count_query = count_query.where(Destination.region == region)

    if is_active is not None:
        query = query.where(Destination.is_active == is_active)
        count_query = count_query.where(Destination.is_active == is_active)

    if is_featured is not None:
        query = query.where(Destination.is_featured == is_featured)
        count_query = count_query.where(Destination.is_featured == is_featured)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(Destination.order), desc(Destination.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    destinations = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [DestinationResponse.model_validate(d).model_dump() for d in destinations],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{destination_id}", response_model=DestinationResponse)
async def get_destination(
    destination_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    dest = result.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return DestinationResponse.model_validate(dest)


@router.post("", response_model=DestinationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_destination(
    request: Request,
    data: DestinationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    import uuid as _uuid

    base_slug = data.name.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(_uuid.uuid4())[:8]}"

    dest = Destination(
        name=data.name,
        slug=slug,
        description=data.description,
        country=data.country,
        region=data.region,
        province=data.province,
        canton=data.canton,
        district=data.district,
        latitude=data.latitude,
        longitude=data.longitude,
        zoom=data.zoom,
        highlights=data.highlights or [],
        things_to_do=data.things_to_do or [],
        culture=data.culture,
        gastronomy=data.gastronomy,
        history=data.history,
        best_time=data.best_time,
        weather_info=data.weather_info,
        getting_there=data.getting_there,
        local_tips=data.local_tips,
        safety_info=data.safety_info,
        language=data.language,
        currency=data.currency,
        timezone=data.timezone,
        phone_code=data.phone_code,
        visa_info=data.visa_info,
        emergency_numbers=data.emergency_numbers or [],
        image=data.image,
        gallery=data.gallery or [],
        videos=data.videos or [],
        featured_photo=data.featured_photo,
        seo_title=data.seo_title,
        seo_description=data.seo_description,
        seo_keywords=data.seo_keywords or [],
        is_featured=data.is_featured,
        is_active=data.is_active,
        order=data.order,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(dest)
    await db.commit()
    await db.refresh(dest)
    return DestinationResponse.model_validate(dest)


@router.put("/{destination_id}", response_model=DestinationResponse)
@limiter.limit("10/minute")
async def update_destination(
    request: Request,
    destination_id: UUID,
    data: DestinationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    dest = result.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    update_data = data.model_dump(exclude_unset=True)
    allowed_fields = {
        "name",
        "slug",
        "description",
        "country",
        "region",
        "province",
        "canton",
        "district",
        "latitude",
        "longitude",
        "zoom",
        "highlights",
        "things_to_do",
        "culture",
        "gastronomy",
        "history",
        "best_time",
        "weather_info",
        "getting_there",
        "local_tips",
        "safety_info",
        "language",
        "currency",
        "timezone",
        "phone_code",
        "visa_info",
        "emergency_numbers",
        "image",
        "gallery",
        "videos",
        "featured_photo",
        "seo_title",
        "seo_description",
        "seo_keywords",
        "is_featured",
        "is_active",
        "order",
    }
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(dest, key, value)

    dest.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(dest)
    return DestinationResponse.model_validate(dest)


@router.delete("/{destination_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_destination(
    request: Request,
    destination_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    dest = result.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    await db.delete(dest)
    await db.commit()
    return {"success": True, "message": "Destination deleted successfully"}


@router.post("/{destination_id}/feature", response_model=dict)
@limiter.limit("10/minute")
async def toggle_destination_featured(
    request: Request,
    destination_id: UUID,
    featured: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Destination).where(Destination.id == destination_id))
    dest = result.scalar_one_or_none()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    dest.is_featured = featured
    dest.updated_at = datetime.now(UTC)
    await db.commit()
    return {
        "success": True,
        "is_featured": dest.is_featured,
        "message": f"Destination {'featured' if featured else 'unfeatured'} successfully",
    }
