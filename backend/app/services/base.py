"""Base service class with soft delete support."""

from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """Base service with soft delete and common CRUD operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: UUID) -> ModelType | None:
        """Get single record by ID, excluding soft-deleted."""
        result = await db.execute(
            select(self.model).where(self.model.id == id, self.model.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        query = select(self.model)
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def count(self, db: AsyncSession, include_deleted: bool = False) -> int:
        """Count records."""
        query = select(func.count(self.model.id))
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        result = await db.execute(query)
        return result.scalar() or 0

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """Create new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, db: AsyncSession, id: UUID) -> bool:
        """Soft delete record."""
        result = await db.execute(
            update(self.model).where(self.model.id == id).values(deleted_at=datetime.now(UTC))
        )
        await db.commit()
        return result.rowcount > 0

    async def restore(self, db: AsyncSession, id: UUID) -> bool:
        """Restore soft-deleted record."""
        result = await db.execute(
            update(self.model).where(self.model.id == id).values(deleted_at=None)
        )
        await db.commit()
        return result.rowcount > 0

    async def hard_delete(self, db: AsyncSession, id: UUID) -> bool:
        """Permanently delete record."""
        result = await db.execute(delete(self.model).where(self.model.id == id))
        await db.commit()
        return result.rowcount > 0
