"""Landing page content API."""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models import Destination, Property, Tour
from app.services.cache_service import cache

router = APIRouter(tags=["Landing"])

CACHE_TTL_LANDING = 180  # 3 minutes for landing content


class LandingDestination(BaseModel):
    id: str
    name: str
    slug: str
    region: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None


class LandingProperty(BaseModel):
    id: str
    name: str
    slug: str
    region: Optional[str] = None
    short_description: Optional[str] = None
    cover_image: Optional[str] = None
    base_price: float = 0
    rating: Optional[float] = None
    property_type: Optional[str] = None


class LandingTour(BaseModel):
    id: str
    name: str
    slug: str
    location: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    price: float = 0
    rating: Optional[float] = None
    duration_text: Optional[str] = None
    duration_hours: float = 0
    category: Optional[str] = None


class LandingContentResponse(BaseModel):
    destinations: list[LandingDestination]
    properties: list[LandingProperty]
    tours: list[LandingTour]


@router.get("/content", response_model=LandingContentResponse)
async def get_landing_content(db: AsyncSession = Depends(get_db)):
    """Get all content for the landing page."""

    cache_key = "landing:content"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Run 3 independent queries in parallel
    async def _get_destinations():
        result = await db.execute(
            select(Destination)
            .where(Destination.is_active, Destination.is_featured)
            .order_by(Destination.order.asc())
            .limit(6)
        )
        return result.scalars().all()

    async def _get_properties():
        result = await db.execute(
            select(Property)
            .where(Property.is_active, Property.is_featured)
            .order_by(Property.rating.desc())
            .limit(6)
        )
        return result.scalars().all()

    async def _get_tours():
        result = await db.execute(
            select(Tour)
            .where(Tour.is_active, Tour.is_featured)
            .order_by(Tour.rating.desc())
            .limit(6)
        )
        return result.scalars().all()

    destinations, properties, tours = (
        await _get_destinations(),
        await _get_properties(),
        await _get_tours(),
    )

    response = {
        "destinations": [
            {
                "id": str(d.id),
                "name": d.name,
                "slug": d.slug,
                "region": d.region,
                "description": d.description,
                "image": d.image,
            }
            for d in destinations
        ],
        "properties": [
            {
                "id": str(p.id),
                "name": p.name,
                "slug": p.slug,
                "region": p.region,
                "short_description": p.short_description,
                "cover_image": p.cover_image,
                "base_price": p.base_price,
                "rating": p.rating,
                "property_type": p.property_type,
            }
            for p in properties
        ],
        "tours": [
            {
                "id": str(t.id),
                "name": t.name,
                "slug": t.slug,
                "location": t.location,
                "description": t.description,
                "cover_image": t.cover_image,
                "price": t.price,
                "rating": t.rating,
                "duration_text": t.duration_text,
                "duration_hours": t.duration_hours,
                "category": t.category,
            }
            for t in tours
        ],
    }

    # Cache the response
    await cache.set(cache_key, response, ttl=CACHE_TTL_LANDING, tags=["landing"])

    return response
