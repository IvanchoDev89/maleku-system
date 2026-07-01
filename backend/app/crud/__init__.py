from datetime import UTC, datetime, timezone
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.pagination import PaginatedResult, PaginationMetadata
from app.schemas import PaginationParams

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """Base CRUD with common operations"""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        filters: dict | None = None,
        eager_load: list[str] | None = None,
    ) -> list[ModelType]:
        query = select(self.model)

        # Apply eager loading for relationships
        if eager_load:
            for relation in eager_load:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_multi_paginated(
        self,
        db: AsyncSession,
        params: PaginationParams,
        order_by: str | None = None,
        filters: dict | None = None,
        eager_load: list[str] | None = None,
    ) -> PaginatedResult:
        """
        Get paginated results with consistent metadata.

        Args:
            db: Database session
            params: Pagination parameters
            order_by: Optional field to order by
            filters: Optional filters to apply
            eager_load: Optional list of relationships to eager load

        Returns:
            PaginatedResult with items and metadata
        """
        query = select(self.model)

        # Apply eager loading
        if eager_load:
            for relation in eager_load:
                if hasattr(self.model, relation):
                    query = query.options(selectinload(getattr(self.model, relation)))

        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        # Count total before pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        # Apply pagination
        query = query.offset(params.offset).limit(params.page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        from math import ceil

        total_pages = ceil(total / params.page_size) if total > 0 else 0

        metadata = PaginationMetadata(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_prev=params.page > 1,
        )

        return PaginatedResult(items=items, pagination=metadata)

    async def get_active(self, db: AsyncSession) -> list[ModelType]:
        if not hasattr(self.model, "is_active"):
            return await self.get_multi(db)
        result = await db.execute(select(self.model).where(self.model.is_active))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, id: UUID, obj_in: dict) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return None
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.now(UTC)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: UUID) -> bool:
        if not hasattr(self.model, "is_active"):
            return False
        result = await db.execute(select(self.model).where(self.model.id == id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            return False
        db_obj.is_active = False
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.now(UTC)
        await db.flush()
        return True

    async def hard_delete(self, db: AsyncSession, id: UUID) -> bool:
        result = await db.execute(delete(self.model).where(self.model.id == id))
        await db.flush()
        return result.rowcount > 0

    async def count(self, db: AsyncSession, filters: dict | None = None) -> int:
        query = select(func.count()).select_from(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        result = await db.execute(query)
        return result.scalar() or 0


class CRUDUser(CRUDBase):
    async def get_by_email(self, db: AsyncSession, email: str) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()

    async def get_by_role(self, db: AsyncSession, role: str) -> list[ModelType]:
        result = await db.execute(select(self.model).where(self.model.role == role))
        return list(result.scalars().all())


class CRUDSlug(CRUDBase):
    async def get_by_slug(self, db: AsyncSession, slug: str) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.slug == slug))
        return result.scalar_one_or_none()


class CRUDRating(CRUDBase):
    async def get_featured(self, db: AsyncSession, limit: int = 10) -> list[ModelType]:
        if not hasattr(self.model, "is_featured"):
            return []
        result = await db.execute(
            select(self.model)
            .where(self.model.is_featured)
            .where(self.model.is_active)
            .order_by(self.model.rating.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_top_rated(self, db: AsyncSession, limit: int = 10) -> list[ModelType]:
        if not hasattr(self.model, "rating"):
            return []
        result = await db.execute(
            select(self.model)
            .where(self.model.is_active)
            .where(self.model.rating > 0)
            .order_by(self.model.rating.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
