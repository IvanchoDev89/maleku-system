from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.utils import escape_like_pattern
from app.models import Property, Tour, Destination, BlogPost, BlogPostStatus

router = APIRouter(tags=["Search"])


class MapPropertyItem(BaseModel):
    id: str
    name: str
    slug: str
    property_type: str
    category: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cover_image: Optional[str] = None
    images: list[str] = []
    base_price: float = 0
    weekend_price: float = 0
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    min_guests: int = 1
    max_guests: int = 10
    amenities: list[str] = []


class MapTourItem(BaseModel):
    id: str
    name: str
    slug: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cover_image: Optional[str] = None
    images: list[str] = []
    price: float = 0
    duration_hours: float = 0
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    max_group_size: int = 20


class MapPagination(BaseModel):
    page: int
    page_size: int
    total_properties: int
    total_tours: int
    total_pages: int


class MapDataResponse(BaseModel):
    properties: list[MapPropertyItem]
    tours: list[MapTourItem]
    pagination: MapPagination


class MapCountsResponse(BaseModel):
    total_properties: int
    total_tours: int
    by_region: dict
    by_category: dict


class SearchResultItem(BaseModel):
    id: str
    name: Optional[str] = None
    title: Optional[str] = None
    slug: str
    type: str
    image: Optional[str] = None


class SearchResponse(BaseModel):
    properties: list[SearchResultItem]
    tours: list[SearchResultItem]
    destinations: list[SearchResultItem]
    blog: list[SearchResultItem]


@router.get(
    "/map",
    response_model=MapDataResponse,
    summary="Get map data",
    description="Returns properties and tours with coordinates for map display. Supports filters by type, category, region, and price range with pagination.",
)
async def get_map_data(
    db: AsyncSession = Depends(get_db),
    property_type: str | None = None,
    category: str | None = None,
    region: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> dict:
    """Get all properties and tours with coordinates for map display"""

    if page_size > 200:
        page_size = 200

    # Build property query
    prop_query = select(Property).where(
        and_(
            Property.is_active,
            Property.latitude.isnot(None),
            Property.longitude.isnot(None),
        )
    )

    if property_type:
        prop_query = prop_query.where(Property.property_type == property_type)
    if category:
        prop_query = prop_query.where(Property.category == category)
    if region:
        prop_query = prop_query.where(Property.region == region)
    if min_price:
        prop_query = prop_query.where(Property.base_price >= min_price)
    if max_price:
        prop_query = prop_query.where(Property.base_price <= max_price)

    count_prop = select(func.count()).select_from(prop_query.subquery())
    total_properties = (await db.execute(count_prop)).scalar()

    offset = (page - 1) * page_size
    prop_query = (
        prop_query.order_by(Property.created_at.desc()).offset(offset).limit(page_size)
    )
    prop_result = await db.execute(prop_query)
    properties = prop_result.scalars().all()

    # Build tour query
    tour_query = select(Tour).where(
        and_(Tour.is_active, Tour.latitude.isnot(None), Tour.longitude.isnot(None))
    )

    if category:
        tour_query = tour_query.where(Tour.category == category)
    if min_price:
        tour_query = tour_query.where(Tour.price >= min_price)
    if max_price:
        tour_query = tour_query.where(Tour.price <= max_price)

    count_tour = select(func.count()).select_from(tour_query.subquery())
    total_tours = (await db.execute(count_tour)).scalar()

    tour_query = (
        tour_query.order_by(Tour.created_at.desc()).offset(offset).limit(page_size)
    )
    tour_result = await db.execute(tour_query)
    tours = tour_result.scalars().all()

    return {
        "properties": [
            {
                "id": str(p.id),
                "name": p.name,
                "slug": p.slug,
                "property_type": p.property_type,
                "category": p.category,
                "region": p.region,
                "city": p.city,
                "address": p.address,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "cover_image": p.cover_image,
                "images": p.images[:4] if p.images else [],
                "base_price": p.base_price,
                "weekend_price": p.weekend_price,
                "rating": p.rating,
                "total_reviews": p.total_reviews,
                "min_guests": p.min_guests,
                "max_guests": p.max_guests,
                "amenities": p.amenities[:8] if p.amenities else [],
            }
            for p in properties
        ],
        "tours": [
            {
                "id": str(t.id),
                "name": t.name,
                "slug": t.slug,
                "category": t.category.value if t.category else None,
                "difficulty": t.difficulty.value if t.difficulty else None,
                "location": t.location,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "cover_image": t.cover_image,
                "images": t.images[:4] if t.images else [],
                "price": t.price,
                "duration_hours": t.duration_hours,
                "rating": t.rating,
                "total_reviews": t.total_reviews,
                "max_group_size": t.max_group_size,
            }
            for t in tours
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_properties": total_properties,
            "total_tours": total_tours,
            "total_pages": max((total_properties + page_size - 1) // page_size, 1),
        },
    }


@router.get(
    "/map/count",
    response_model=MapCountsResponse,
    summary="Get map counts",
    description="Returns aggregate counts for map markers: total properties/tours, grouped by region and category.",
)
async def get_map_counts(db: AsyncSession = Depends(get_db)) -> dict:
    """Get counts for map markers and stats"""

    # Count properties by region
    prop_result = await db.execute(
        select(Property.region, func.count())
        .where(Property.is_active)
        .group_by(Property.region)
    )

    regions = {}
    for row in prop_result.all():
        if row[0]:
            regions[row[0]] = row[1]

    # Count tours by category
    tour_result = await db.execute(
        select(Tour.category, func.count())
        .where(Tour.is_active)
        .group_by(Tour.category)
    )

    categories = {}
    for row in tour_result.all():
        if row[0]:
            categories[row[0].value] = row[1]

    # Total counts
    total_properties = await db.execute(
        select(func.count()).select_from(Property).where(Property.is_active)
    )
    total_tours = await db.execute(
        select(func.count()).select_from(Tour).where(Tour.is_active)
    )

    return {
        "total_properties": total_properties.scalar() or 0,
        "total_tours": total_tours.scalar() or 0,
        "by_region": regions,
        "by_category": categories,
    }


@router.get(
    "",
    response_model=SearchResponse,
    summary="Global search",
    description="Searches properties, tours, destinations, and blog in parallel using ILIKE pattern matching on names/titles.",
)
async def global_search(
    q: str = Query(..., min_length=1, max_length=200),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
) -> dict:
    # Sanitize query input
    q = q.strip()[:200]

    # Search properties, tours, destinations, blog in parallel
    pattern = f"%{escape_like_pattern(q)}%"

    async def _search_properties():
        result = await db.execute(
            select(Property)
            .where(Property.is_active)
            .where(Property.name.ilike(pattern))
            .limit(limit)
        )
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "slug": p.slug,
                "type": "property",
                "image": p.images[0] if p.images else None,
            }
            for p in result.scalars().all()
        ]

    async def _search_tours():
        result = await db.execute(
            select(Tour)
            .where(Tour.is_active)
            .where(Tour.name.ilike(pattern))
            .limit(limit)
        )
        return [
            {
                "id": str(t.id),
                "name": t.name,
                "slug": t.slug,
                "type": "tour",
                "image": t.cover_image,
            }
            for t in result.scalars().all()
        ]

    async def _search_destinations():
        result = await db.execute(
            select(Destination)
            .where(Destination.is_active)
            .where(Destination.name.ilike(pattern))
            .limit(limit)
        )
        return [
            {
                "id": str(d.id),
                "name": d.name,
                "slug": d.slug,
                "type": "destination",
                "image": d.image,
            }
            for d in result.scalars().all()
        ]

    async def _search_blog():
        result = await db.execute(
            select(BlogPost)
            .where(BlogPost.status == BlogPostStatus.PUBLISHED)
            .where(BlogPost.title.ilike(pattern))
            .limit(limit)
        )
        return [
            {
                "id": str(b.id),
                "title": b.title,
                "slug": b.slug,
                "type": "blog",
                "image": b.featured_image,
            }
            for b in result.scalars().all()
        ]

    props, tours_res, dests, blog = (
        await _search_properties(),
        await _search_tours(),
        await _search_destinations(),
        await _search_blog(),
    )

    return {
        "properties": props,
        "tours": tours_res,
        "destinations": dests,
        "blog": blog,
    }
