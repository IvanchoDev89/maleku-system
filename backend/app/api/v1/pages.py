from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.content import StaticPage as StaticPageModel
from app.schemas.content import StaticPageResponse as StaticPageResponseSchema

router = APIRouter(prefix="/pages", tags=["Pages"])


@router.get("/public", response_model=list[StaticPageResponseSchema])
async def list_public_pages(
    db: AsyncSession = Depends(get_db),
):
    """List all active static pages for public consumption."""
    result = await db.execute(
        select(StaticPageModel)
        .where(StaticPageModel.is_active == True)
        .order_by(StaticPageModel.sort_order, StaticPageModel.title)
    )
    return result.scalars().all()


@router.get("/public/{slug}", response_model=StaticPageResponseSchema)
async def get_public_page(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single active static page by slug."""
    result = await db.execute(
        select(StaticPageModel).where(
            StaticPageModel.slug == slug, StaticPageModel.is_active == True
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page
