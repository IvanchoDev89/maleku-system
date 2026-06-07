"""
Pagination utilities for consistent API responses
"""
from typing import TypeVar, Generic, List, Optional
from math import ceil
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginationParams:
    """Common pagination parameters for API endpoints"""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    ):
        self.page = page
        self.page_size = page_size
        
    @property
    def offset(self) -> int:
        """Calculate database offset"""
        return (self.page - 1) * self.page_size


class PaginationMetadata(BaseModel):
    """Pagination metadata for API responses"""
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResult(BaseModel, Generic[T]):
    """Generic paginated result container"""
    items: List[T]
    pagination: PaginationMetadata


async def paginate_query(
    session: AsyncSession,
    query,
    params: PaginationParams,
    transform_func: Optional[callable] = None
) -> PaginatedResult:
    """
    Execute a query with pagination.
    
    Args:
        session: Database session
        query: SQLAlchemy select query
        params: Pagination parameters
        transform_func: Optional function to transform each result item
        
    Returns:
        PaginatedResult with items and metadata
    """
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination to query
    paginated_query = query.offset(params.offset).limit(params.page_size)
    result = await session.execute(paginated_query)
    items = result.scalars().all()
    
    # Transform items if needed
    if transform_func:
        items = [transform_func(item) for item in items]
    
    # Calculate metadata
    total_pages = ceil(total / params.page_size) if total > 0 else 0
    
    metadata = PaginationMetadata(
        page=params.page,
        page_size=params.page_size,
        total=total,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1
    )
    
    return PaginatedResult(
        items=items,
        pagination=metadata
    )


async def paginate_list(
    items: List[T],
    params: PaginationParams
) -> PaginatedResult:
    """
    Paginate an in-memory list.
    
    Args:
        items: List of items
        params: Pagination parameters
        
    Returns:
        PaginatedResult with items and metadata
    """
    total = len(items)
    start = params.offset
    end = start + params.page_size
    paginated_items = items[start:end]
    
    total_pages = ceil(total / params.page_size) if total > 0 else 0
    
    metadata = PaginationMetadata(
        page=params.page,
        page_size=params.page_size,
        total=total,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1
    )
    
    return PaginatedResult(
        items=paginated_items,
        pagination=metadata
    )
