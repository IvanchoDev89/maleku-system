"""
Super Admin Content Management API

Manages blog posts, static pages, SEO settings, and media library.
Exclusive access for SUPER_ADMIN role.
"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.models import BlogPost as BlogPostModel
from app.models import User
from app.models.audit import AuditAction
from app.models.content import MediaFile as MediaFileModel
from app.models.content import SEOSettings as SEOSettingsModel
from app.models.content import StaticPage as StaticPageModel
from app.schemas import BlogPostCreate as BlogPostCreateSchema
from app.schemas import BlogPostUpdate as BlogPostUpdateSchema
from app.schemas.content import (
    MediaFileResponse as MediaFileResponseSchema,
)
from app.schemas.content import (
    SEOSettingsResponse as SEOSettingsResponseSchema,
)
from app.schemas.content import (
    SEOSettingsUpdate as SEOSettingsUpdateSchema,
)
from app.schemas.content import (
    StaticPageCreate as StaticPageCreateSchema,
)
from app.schemas.content import (
    StaticPageResponse as StaticPageResponseSchema,
)
from app.schemas.content import (
    StaticPageUpdate as StaticPageUpdateSchema,
)
from app.services.audit_service import AuditService

router = APIRouter(prefix="/content", tags=["Super Admin - Content"])


def _serialize_for_audit(data: dict) -> dict:
    """Convert non-JSON-serializable values (datetime, UUID, etc.) to strings."""
    result = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, UUID):
            result[k] = str(v)
        elif isinstance(v, list):
            result[k] = [str(i) if isinstance(i, UUID) else i for i in v]
        elif hasattr(v, "isoformat"):
            result[k] = str(v)
        else:
            result[k] = v
    return result


def _format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


async def _get_or_create_seo(db: AsyncSession) -> SEOSettingsModel:
    """Get the first SEO settings row, creating defaults if none exists."""
    result = await db.execute(select(SEOSettingsModel).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = SEOSettingsModel()
        db.add(settings)
        await db.flush()
    return settings


# ---- Blog posts ----


@router.get("/blog", response_model=list[dict])
async def list_blog_posts(
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None, max_length=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """List all blog posts with filtering"""
    query = select(BlogPostModel).where(BlogPostModel.deleted_at.is_(None))
    count_query = select(func.count(BlogPostModel.id)).where(BlogPostModel.deleted_at.is_(None))

    if status_filter:
        query = query.where(BlogPostModel.status == status_filter)
        count_query = count_query.where(BlogPostModel.status == status_filter)

    if search:
        like = f"%{search}%"
        query = query.where(BlogPostModel.title.ilike(like))
        count_query = count_query.where(BlogPostModel.title.ilike(like))

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(BlogPostModel.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()

    return [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "excerpt": p.excerpt,
            "category": p.category,
            "status": p.status,
            "views_count": p.views_count,
            "is_featured": p.is_featured,
            "author_name": p.author.full_name if p.author else None,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "published_at": p.published_at.isoformat() if p.published_at else None,
        }
        for p in posts
    ]


@router.get("/blog/{post_id}", response_model=dict)
async def get_blog_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get single blog post"""
    result = await db.execute(
        select(BlogPostModel).where(BlogPostModel.id == post_id, BlogPostModel.deleted_at.is_(None))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    return {
        "id": str(post.id),
        "title": post.title,
        "slug": post.slug,
        "excerpt": post.excerpt,
        "content": post.content,
        "featured_image": post.featured_image,
        "category": post.category,
        "tags": post.tags or [],
        "author_id": str(post.author_id) if post.author_id else None,
        "author_name": post.author.full_name if post.author else None,
        "status": post.status,
        "views_count": post.views_count,
        "is_featured": post.is_featured,
        "seo_title": post.seo_title,
        "seo_description": post.seo_description,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


@router.post("/blog", response_model=dict, status_code=201)
@limiter.limit("10/minute")
async def create_blog_post(
    request: Request,
    data: BlogPostCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Create new blog post"""
    import uuid as _uuid

    base_slug = data.title.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(_uuid.uuid4())[:8]}"

    post = BlogPostModel(
        title=data.title,
        slug=slug,
        excerpt=data.excerpt,
        content=data.content,
        category=data.category,
        featured_image=getattr(data, "featured_image", None),
        tags=getattr(data, "tags", None) or [],
        author_id=current_user.id,
        status="draft",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    if hasattr(data, "status") and data.status:
        post.status = data.status
    if data.published_at:
        post.published_at = data.published_at

    db.add(post)
    await db.flush()

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.CREATE,
        entity_type="blog_post",
        entity_id=post.id,
        entity_name=post.title,
        new_values={"title": post.title, "status": post.status},
        changes_summary=f"Blog post '{post.title}' created",
    )

    await db.commit()
    await db.refresh(post)

    return {"success": True, "id": str(post.id), "slug": post.slug}


@router.put("/blog/{post_id}", response_model=dict)
@limiter.limit("10/minute")
async def update_blog_post(
    request: Request,
    post_id: UUID,
    data: BlogPostUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update blog post"""
    result = await db.execute(
        select(BlogPostModel).where(BlogPostModel.id == post_id, BlogPostModel.deleted_at.is_(None))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    old_title = post.title
    update_data = data.model_dump(exclude_unset=True)
    allowed_fields = {
        "title",
        "excerpt",
        "content",
        "featured_image",
        "category",
        "tags",
        "status",
        "published_at",
        "seo_title",
        "seo_description",
    }
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(post, key, value)

    post.updated_at = datetime.now(UTC)
    await db.flush()

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="blog_post",
        entity_id=post.id,
        entity_name=post.title,
        old_values={"title": old_title},
        new_values={"title": post.title, "status": post.status},
        changes_summary=f"Blog post '{post.title}' updated",
    )

    await db.commit()
    return {"success": True, "message": "Blog post updated"}


@router.delete("/blog/{post_id}", response_model=dict, status_code=200)
async def delete_blog_post(
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Soft delete blog post"""
    result = await db.execute(
        select(BlogPostModel).where(BlogPostModel.id == post_id, BlogPostModel.deleted_at.is_(None))
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    post.deleted_at = datetime.now(UTC)
    await db.flush()

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="blog_post",
        entity_id=post.id,
        entity_name=post.title,
        old_values={"title": post.title, "status": post.status},
        changes_summary=f"Blog post '{post.title}' deleted",
    )

    await db.commit()
    return {"success": True, "message": "Blog post deleted"}


# ---- Static Pages ----


@router.get("/pages", response_model=list[StaticPageResponseSchema])
async def list_static_pages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """List all static pages"""
    result = await db.execute(
        select(StaticPageModel).order_by(StaticPageModel.sort_order, StaticPageModel.title)
    )
    pages = result.scalars().all()
    return pages


@router.get("/pages/{page_id}", response_model=StaticPageResponseSchema)
async def get_static_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get single static page"""
    result = await db.execute(select(StaticPageModel).where(StaticPageModel.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.post("/pages", response_model=StaticPageResponseSchema, status_code=201)
@limiter.limit("10/minute")
async def create_static_page(
    request: Request,
    data: StaticPageCreateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Create new static page"""
    existing = await db.execute(select(StaticPageModel).where(StaticPageModel.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A page with this slug already exists")

    page = StaticPageModel(
        title=data.title,
        slug=data.slug,
        content=data.content,
        template=data.template,
        meta_title=data.meta_title,
        meta_description=data.meta_description,
        is_active=data.is_active,
        show_in_footer=data.show_in_footer,
        show_in_header=data.show_in_header,
        sort_order=data.sort_order,
    )
    db.add(page)
    await db.flush()

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.CREATE,
        entity_type="static_page",
        entity_id=page.id,
        entity_name=page.title,
        new_values={"title": page.title, "slug": page.slug},
        changes_summary=f"Static page '{page.title}' created",
    )

    await db.commit()
    await db.refresh(page)
    return page


@router.put("/pages/{page_id}", response_model=StaticPageResponseSchema)
@limiter.limit("10/minute")
async def update_static_page(
    request: Request,
    page_id: UUID,
    data: StaticPageUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update static page"""
    result = await db.execute(select(StaticPageModel).where(StaticPageModel.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    old_values = {
        "title": page.title,
        "slug": page.slug,
        "content": page.content,
        "is_active": page.is_active,
        "show_in_footer": page.show_in_footer,
        "show_in_header": page.show_in_header,
    }

    update_data = data.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != page.slug:
        existing = await db.execute(
            select(StaticPageModel).where(
                StaticPageModel.slug == update_data["slug"],
                StaticPageModel.id != page_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="A page with this slug already exists")

    allowed_fields = {
        "title",
        "slug",
        "content",
        "template",
        "meta_title",
        "meta_description",
        "is_active",
        "show_in_footer",
        "show_in_header",
        "sort_order",
    }
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(page, key, value)

    page.updated_at = datetime.now(UTC)
    await db.flush()

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="static_page",
        entity_id=page.id,
        entity_name=page.title,
        old_values=_serialize_for_audit(old_values),
        new_values=_serialize_for_audit(
            {
                "title": page.title,
                "slug": page.slug,
                "is_active": page.is_active,
            }
        ),
        changes_summary=f"Static page '{page.title}' updated",
    )

    await db.commit()
    await db.refresh(page)
    return page


@router.delete("/pages/{page_id}", status_code=204)
async def delete_static_page(
    page_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Delete static page"""
    result = await db.execute(select(StaticPageModel).where(StaticPageModel.id == page_id))
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="static_page",
        entity_id=page.id,
        entity_name=page.title,
        old_values={"title": page.title, "slug": page.slug},
        changes_summary=f"Static page '{page.title}' deleted",
    )

    await db.delete(page)
    await db.commit()


# ---- SEO Settings ----


@router.get("/seo", response_model=SEOSettingsResponseSchema)
async def get_seo_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get global SEO settings"""
    settings = await _get_or_create_seo(db)
    return settings


@router.put("/seo", response_model=SEOSettingsResponseSchema)
@limiter.limit("10/minute")
async def update_seo_settings(
    request: Request,
    data: SEOSettingsUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update global SEO settings"""
    settings = await _get_or_create_seo(db)

    old_values = {
        "site_title_template": settings.site_title_template,
        "default_meta_title": settings.default_meta_title,
        "default_meta_description": settings.default_meta_description,
        "sitemap_enabled": settings.sitemap_enabled,
        "structured_data_enabled": settings.structured_data_enabled,
    }

    update_data = data.model_dump(exclude_unset=True)
    allowed_fields = {
        "site_title_template",
        "default_meta_title",
        "default_meta_description",
        "default_meta_keywords",
        "google_site_verification",
        "robots_txt",
        "sitemap_enabled",
        "structured_data_enabled",
    }
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(settings, key, value)

    settings.updated_by = current_user.id
    settings.updated_at = datetime.now(UTC)
    await db.flush()

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="seo_settings",
        entity_id=settings.id,
        entity_name="Global SEO Settings",
        old_values=_serialize_for_audit(old_values),
        new_values=_serialize_for_audit(update_data),
        changes_summary="SEO settings updated",
    )

    await db.commit()
    await db.refresh(settings)
    return settings


# ---- Media Files ----


@router.get("/media", response_model=list[MediaFileResponseSchema])
async def list_media(
    folder: str | None = Query(None, max_length=100),
    mime_type: str | None = Query(None, max_length=50),
    search: str | None = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """List media files"""
    query = select(MediaFileModel)
    count_query = select(func.count(MediaFileModel.id))

    if folder:
        query = query.where(MediaFileModel.folder == folder)
        count_query = count_query.where(MediaFileModel.folder == folder)
    if mime_type:
        query = query.where(MediaFileModel.mime_type.startswith(mime_type))
        count_query = count_query.where(MediaFileModel.mime_type.startswith(mime_type))
    if search:
        like = f"%{search}%"
        query = query.where(MediaFileModel.filename.ilike(like))
        count_query = count_query.where(MediaFileModel.filename.ilike(like))

    query = query.order_by(desc(MediaFileModel.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    media_files = result.scalars().all()

    return [
        MediaFileResponseSchema(
            id=m.id,
            filename=m.filename,
            original_name=m.original_name,
            mime_type=m.mime_type,
            size_bytes=m.size_bytes,
            size_formatted=_format_size(m.size_bytes),
            url=m.url,
            thumbnail_url=m.thumbnail_url,
            alt_text=m.alt_text,
            folder=m.folder,
            uploaded_by=m.uploader.email if m.uploader else None,
            created_at=m.created_at,
            used_in=m.used_in or [],
        )
        for m in media_files
    ]


@router.delete("/media/{media_id}", status_code=204)
async def delete_media(
    media_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Delete media file"""
    result = await db.execute(select(MediaFileModel).where(MediaFileModel.id == media_id))
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media file not found")

    if media.used_in:
        raise HTTPException(
            status_code=400,
            detail=f"Media is used in {len(media.used_in)} places. Remove references first.",
        )

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="media",
        entity_id=media.id,
        entity_name=media.filename,
        old_values={"filename": media.filename, "url": media.url},
        changes_summary=f"Media file '{media.filename}' deleted",
    )

    await db.delete(media)
    await db.commit()
