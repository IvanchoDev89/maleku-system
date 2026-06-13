"""Full-text search service using PostgreSQL."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.property import Property
from app.models.tour import Tour
from app.models.blog import BlogPost


class SearchResult:
    """Search result with ranking."""

    def __init__(self, item, rank: float):
        self.item = item
        self.rank = rank


class SearchService:
    """Full-text search using PostgreSQL tsvector."""

    async def search_properties(
        self,
        db: AsyncSession,
        query: str,
        amenities: Optional[List[str]] = None,
        region: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20,
    ) -> List[SearchResult]:
        """Search properties with text ranking and filters."""

        # Build tsquery from plain text
        tsquery = func.plainto_tsquery("spanish", query)

        # Full-text search with ranking
        tsvector = func.to_tsvector(
            "spanish",
            func.coalesce(Property.name, "")
            + " "
            + func.coalesce(Property.short_description, "")
            + " "
            + func.coalesce(Property.description, "")
            + " "
            + func.coalesce(Property.city, "")
            + " "
            + func.coalesce(Property.region, ""),
        )

        stmt = select(Property, func.ts_rank(tsvector, tsquery).label("rank")).where(
            and_(
                tsvector.op("@@")(tsquery),
                Property.deleted_at.is_(None),
                Property.is_active,
            )
        )

        # Apply filters
        if amenities:
            stmt = stmt.where(Property.amenities.op("@>")(amenities))
        if region:
            stmt = stmt.where(Property.region.ilike(f"%{region}%"))
        if min_price:
            stmt = stmt.where(Property.base_price >= min_price)
        if max_price:
            stmt = stmt.where(Property.base_price <= max_price)

        stmt = stmt.order_by("rank DESC").limit(limit)

        result = await db.execute(stmt)
        rows = result.all()

        return [SearchResult(row[0], row[1]) for row in rows]

    async def search_tours(
        self,
        db: AsyncSession,
        query: str,
        category: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 20,
    ) -> List[SearchResult]:
        """Search tours with text ranking."""

        tsquery = func.plainto_tsquery("spanish", query)

        tsvector = func.to_tsvector(
            "spanish",
            func.coalesce(Tour.name, "")
            + " "
            + func.coalesce(Tour.description, "")
            + " "
            + func.coalesce(Tour.location, ""),
        )

        stmt = select(Tour, func.ts_rank(tsvector, tsquery).label("rank")).where(
            and_(tsvector.op("@@")(tsquery), Tour.deleted_at.is_(None), Tour.is_active)
        )

        if category:
            stmt = stmt.where(Tour.category == category)
        if location:
            stmt = stmt.where(Tour.location.ilike(f"%{location}%"))

        stmt = stmt.order_by("rank DESC").limit(limit)

        result = await db.execute(stmt)
        rows = result.all()

        return [SearchResult(row[0], row[1]) for row in rows]

    async def search_blog(
        self,
        db: AsyncSession,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[SearchResult]:
        """Search blog posts with text ranking."""

        tsquery = func.plainto_tsquery("spanish", query)

        tsvector = func.to_tsvector(
            "spanish",
            func.coalesce(BlogPost.title, "")
            + " "
            + func.coalesce(BlogPost.content, "")
            + " "
            + func.coalesce(BlogPost.excerpt, ""),
        )

        stmt = select(BlogPost, func.ts_rank(tsvector, tsquery).label("rank")).where(
            and_(
                tsvector.op("@@")(tsquery),
                BlogPost.deleted_at.is_(None),
                BlogPost.status == "published",
            )
        )

        if category:
            stmt = stmt.where(BlogPost.category == category)

        stmt = stmt.order_by("rank DESC").limit(limit)

        result = await db.execute(stmt)
        rows = result.all()

        return [SearchResult(row[0], row[1]) for row in rows]
