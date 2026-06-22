import re
import uuid
from datetime import datetime, timezone
from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_role
from app.core.utils import escape_like_pattern
from app.schemas import (
    DestinationResponse,
    DestinationCreate,
    DestinationUpdate,
    PaginatedResponse,
)
from app.models import User, UserRole, Destination
from app.services.cache_service import cache

router = APIRouter(tags=["Destinations"])

CACHE_TTL_LIST = 600
CACHE_TTL_DETAIL = 900

VALID_SORT_FIELDS = {"order", "name", "created_at", "region", "province", "is_featured"}

ALLOWED_FIELDS = {
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


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


@router.get(
    "",
    response_model=Union[list[DestinationResponse], PaginatedResponse],
    summary="List destinations with optional pagination",
)
async def get_destinations(
    db: AsyncSession = Depends(get_db),
    region: Optional[str] = Query(None, description="Filter by region"),
    featured: Optional[bool] = Query(None, description="Filter featured only"),
    province: Optional[str] = Query(None, description="Filter by province"),
    search: Optional[str] = Query(None, description="Search name/description"),
    active_only: bool = Query(True, description="Exclude inactive"),
    page: int = Query(1, ge=1, description="Page number (requires page_size)"),
    page_size: int = Query(
        0, ge=0, le=100, description="Items per page; 0 = flat list"
    ),
    sort_by: str = Query("order", description="Sort field"),
    sort_order: str = Query("asc", description="asc or desc"),
):
    if sort_by not in VALID_SORT_FIELDS:
        sort_by = "order"
    if sort_order not in ("asc", "desc"):
        sort_order = "asc"

    paginated = page_size > 0

    cache_key = None
    if not paginated:
        cache_key = (
            f"destinations:list:{region}:{featured}:{province}:{search}:{active_only}"
        )
        cached = await cache.get(cache_key)
        if cached:
            return [DestinationResponse(**item) for item in cached]

    query = select(Destination)
    query = query.where(Destination.deleted_at.is_(None))
    if active_only:
        query = query.where(Destination.is_active)
    if region:
        query = query.where(Destination.region == region)
    if featured is not None:
        query = query.where(Destination.is_featured == featured)
    if province:
        query = query.where(Destination.province == province)
    if search:
        safe_search = escape_like_pattern(search)
        like = f"%{safe_search}%"
        query = query.where(
            Destination.name.ilike(like) | Destination.description.ilike(like)
        )

    total = 0
    if paginated:
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

    sort_col = getattr(Destination, sort_by, Destination.order)
    if sort_order == "desc":
        sort_col = sort_col.desc()
    query = query.order_by(sort_col, Destination.name.asc())

    if paginated:
        query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    destinations = result.scalars().all()
    items = [DestinationResponse.model_validate(d) for d in destinations]

    if paginated:
        total_pages = max(1, (total + page_size - 1) // page_size)
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page * page_size < total,
            has_prev=page > 1,
        )

    if cache_key:
        await cache.set(
            cache_key,
            [item.model_dump() for item in items],
            ttl=CACHE_TTL_LIST,
            tags=["destinations"],
        )
    return items


@router.get(
    "/hierarchy",
    response_model=list[dict],
    summary="Geographic hierarchy tree",
)
async def get_destination_hierarchy(db: AsyncSession = Depends(get_db)):
    cache_key = "destinations:hierarchy"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(Destination.region, Destination.province, func.count(Destination.id))
        .where(Destination.is_active, Destination.deleted_at.is_(None))
        .group_by(Destination.region, Destination.province)
        .order_by(Destination.region, Destination.province)
    )
    rows = result.all()

    tree: dict[str, dict] = {}
    for region, province, count in rows:
        region = region or "Other"
        province = province or "Other"
        if region not in tree:
            tree[region] = {"name": region, "children": []}
        tree[region]["children"].append({"name": province, "count": count})

    hierarchy = list(tree.values())
    await cache.set(cache_key, hierarchy, ttl=CACHE_TTL_LIST, tags=["destinations"])
    return hierarchy


@router.get(
    "/{destination_id_or_slug}",
    response_model=DestinationResponse,
    summary="Get destination by ID or slug",
)
async def get_destination(
    destination_id_or_slug: str, db: AsyncSession = Depends(get_db)
):
    try:
        dest_id = uuid.UUID(destination_id_or_slug)
        cache_key = f"destinations:detail:{dest_id}"
        query = select(Destination).where(
            Destination.id == dest_id, Destination.deleted_at.is_(None)
        )
    except ValueError:
        cache_key = f"destinations:slug:{destination_id_or_slug}"
        query = select(Destination).where(
            Destination.slug == destination_id_or_slug, Destination.deleted_at.is_(None)
        )

    cached = await cache.get(cache_key)
    if cached:
        return DestinationResponse(**cached)

    result = await db.execute(query)
    destination = result.scalar_one_or_none()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found"
        )

    response = DestinationResponse.model_validate(destination)
    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["destinations", f"destination:{destination.id}"],
    )
    return response


@router.post(
    "",
    response_model=DestinationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create destination",
)
@limiter.limit("10/minute")
async def create_destination(
    request: Request,
    data: DestinationCreate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    payload = data.model_dump(exclude_unset=True)
    slug = payload.pop("slug", None) or slugify(payload.get("name", ""))

    destination_data = {k: v for k, v in payload.items() if k in ALLOWED_FIELDS}
    destination = Destination(slug=slug, **destination_data)
    db.add(destination)
    await db.flush()
    await db.commit()

    await cache.invalidate_tag("destinations")
    return DestinationResponse.model_validate(destination)


@router.put(
    "/{destination_id}",
    response_model=DestinationResponse,
    summary="Update destination",
)
@limiter.limit("10/minute")
async def update_destination(
    request: Request,
    destination_id: uuid.UUID,
    data: DestinationUpdate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    destination = result.scalar_one_or_none()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found"
        )

    patch = data.model_dump(exclude_unset=True)
    if "slug" in patch and not patch["slug"]:
        patch["slug"] = slugify(patch.get("name", destination.name))

    for field, value in patch.items():
        if field in ALLOWED_FIELDS or field == "slug":
            setattr(destination, field, value)

    await db.flush()
    await db.commit()

    await cache.invalidate_tag("destinations")
    await cache.invalidate_tag(f"destination:{destination_id}")
    await cache.delete(f"destinations:detail:{destination_id}")
    await cache.delete(f"destinations:slug:{destination.slug}")

    return DestinationResponse.model_validate(destination)


@router.delete(
    "/{destination_id}",
    response_model=dict,
    summary="Delete destination (soft)",
)
async def delete_destination(
    destination_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    destination = result.scalar_one_or_none()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found"
        )

    destination.is_active = False
    destination.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    await db.commit()

    await cache.invalidate_tag("destinations")
    await cache.invalidate_tag(f"destination:{destination_id}")
    await cache.delete(f"destinations:detail:{destination_id}")
    await cache.delete(f"destinations:slug:{destination.slug}")

    return {"message": "Destination deleted successfully"}


@router.put(
    "/{destination_id}/order",
    response_model=dict,
    summary="Reorder destination",
)
@limiter.limit("10/minute")
async def reorder_destination(
    request: Request,
    destination_id: uuid.UUID,
    order: int,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Destination).where(Destination.id == destination_id)
    )
    destination = result.scalar_one_or_none()

    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found"
        )

    destination.order = order
    await db.flush()
    await db.commit()

    await cache.invalidate_tag("destinations")
    return {"message": "Destination order updated"}
