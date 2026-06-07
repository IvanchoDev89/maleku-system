"""Landing page content API."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Destination, Property, Tour
from app.services.cache_service import cache

router = APIRouter(tags=["Landing"])

CACHE_TTL_LANDING = 180  # 3 minutes for landing content


@router.get("/content")
async def get_landing_content(
    db: AsyncSession = Depends(get_db)
):
    """Get all content for the landing page."""

    cache_key = "landing:content"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Get featured destinations
    dest_query = select(Destination).where(
        Destination.is_active,
        Destination.is_featured
    ).order_by(Destination.order.asc()).limit(6)
    dest_result = await db.execute(dest_query)
    destinations = dest_result.scalars().all()

    # Get featured properties (hotels)
    prop_query = select(Property).where(
        Property.is_active,
        Property.is_featured
    ).order_by(Property.rating.desc()).limit(6)
    prop_result = await db.execute(prop_query)
    properties = prop_result.scalars().all()

    # Get featured tours
    tour_query = select(Tour).where(
        Tour.is_active,
        Tour.is_featured
    ).order_by(Tour.rating.desc()).limit(6)
    tour_result = await db.execute(tour_query)
    tours = tour_result.scalars().all()

    response = {
        "destinations": [
            {
                "id": str(d.id),
                "name": d.name,
                "slug": d.slug,
                "region": d.region,
                "description": d.description,
                "image": d.image
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
                "property_type": p.property_type.value if p.property_type else None
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
                "category": t.category.value if t.category else None
            }
            for t in tours
        ]
    }

    # Cache the response
    await cache.set(cache_key, response, ttl=CACHE_TTL_LANDING, tags=["landing"])

    return response