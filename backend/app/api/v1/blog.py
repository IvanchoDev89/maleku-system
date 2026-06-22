import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.pagination import paginate_flat
from app.core.security import require_role
from app.core.logging import get_logger
from app.models import User, UserRole, BlogPost, BlogPostStatus
from app.schemas import (
    BlogPostResponse,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostListResponse,
    PaginationParams,
    PaginatedResponse,
)
from app.core.config import settings
from app.services.cache_service import cache
from pydantic import BaseModel

router = APIRouter(tags=["Blog"])


class DeleteResponse(BaseModel):
    message: str


class BlogCategoriesResponse(BaseModel):
    categories: list[str]


limiter = Limiter(key_func=get_remote_address, enabled=settings.ENVIRONMENT != "test")


def _sanitize_cache_key(value: str) -> str:
    """Sanitize value for use in cache key to prevent injection."""
    if not value:
        return ""
    # Remove any characters that could cause cache key issues
    return re.sub(r"[^a-zA-Z0-9_-]", "", value)[:50]  # Limit length


CACHE_TTL_LIST = 300  # 5 minutes for blog lists
CACHE_TTL_DETAIL = 600  # 10 minutes for blog posts
CACHE_TTL_FEATURED = 180  # 3 minutes for featured posts


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List blog posts",
    description="Paginated list of blog posts with optional filters by category and status.",
)
async def get_blog_posts(
    params: PaginationParams = Depends(),
    category: str = None,
    status: str = "published",
    db: AsyncSession = Depends(get_db),
):
    # SECURITY: Sanitize cache key parameters to prevent injection
    safe_category = _sanitize_cache_key(category) if category else "all"
    safe_status = _sanitize_cache_key(status) if status else "published"
    cache_key = (
        f"blog:list:{safe_category}:{safe_status}:{params.page}:{params.page_size}"
    )

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return PaginatedResponse(**cached)

    query = select(BlogPost)

    if status:
        query = query.where(BlogPost.status == BlogPostStatus(status))
    if category:
        query = query.where(BlogPost.category == category)

    response = await paginate_flat(
        db,
        query,
        params,
        transform_func=BlogPostListResponse.model_validate,
        order_by=BlogPost.published_at.desc().nulls_last(),
    )

    # Cache the response
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_LIST, tags=["blog"])

    return response


@router.get(
    "/featured",
    response_model=list[BlogPostListResponse],
    summary="Get featured posts",
    description="Returns featured blog posts, ordered by published date. Default limit is 3.",
)
async def get_featured_posts(db: AsyncSession = Depends(get_db), limit: int = 3):
    cache_key = f"blog:featured:{limit}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return [BlogPostListResponse(**item) for item in cached]

    result = await db.execute(
        select(BlogPost)
        .where(BlogPost.status == BlogPostStatus.PUBLISHED)
        .where(BlogPost.is_featured)
        .order_by(BlogPost.published_at.desc())
        .limit(limit)
    )
    posts = result.scalars().all()
    response = [BlogPostListResponse.model_validate(p) for p in posts]

    # Cache the response
    await cache.set(
        cache_key,
        [item.model_dump() for item in response],
        ttl=CACHE_TTL_FEATURED,
        tags=["blog", "blog:featured"],
    )

    return response


@router.get(
    "/{post_id}",
    response_model=BlogPostResponse,
    summary="Get blog post by ID",
    description="Returns a single blog post by UUID. Increments the view counter.",
)
async def get_blog_post(post_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cache_key = f"blog:detail:{post_id}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return BlogPostResponse(**cached)

    result = await db.execute(
        select(BlogPost)
        .where(BlogPost.id == post_id)
        .options(selectinload(BlogPost.author))
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found"
        )

    response = BlogPostResponse.model_validate(post)
    response.author_name = post.author.name if post.author else None

    # Increment views asynchronously (non-blocking)
    post.views_count += 1
    await db.flush()
    await db.commit()

    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["blog", f"blog:{post.id}"],
    )
    return response


@router.get(
    "/slug/{slug}",
    response_model=BlogPostResponse,
    summary="Get blog post by slug",
    description="Returns a single blog post by URL-friendly slug. Increments the view counter.",
)
async def get_blog_post_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    safe_slug = _sanitize_cache_key(slug)
    cache_key = f"blog:slug:{safe_slug}"

    cached = await cache.get(cache_key)
    if cached:
        return BlogPostResponse(**cached)

    result = await db.execute(
        select(BlogPost)
        .where(BlogPost.slug == slug)
        .options(selectinload(BlogPost.author))
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found"
        )

    post.views_count += 1
    await db.flush()
    await db.commit()

    response = BlogPostResponse.model_validate(post)
    response.author_name = post.author.name if post.author else None
    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["blog", f"blog:{post.id}"],
    )

    return response


@router.post(
    "",
    response_model=BlogPostResponse,
    summary="Create blog post",
    description="Creates a new blog post as DRAFT. SUPER_ADMIN or VENDOR role required. Rate limited to 30/minute.",
)
@limiter.limit("30/minute")  # Rate limiting: 30 posts por minuto
async def create_blog_post(
    request: Request,
    data: BlogPostCreate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.VENDOR)),
    db: AsyncSession = Depends(get_db),
):
    slug = slugify(data.title)

    # Ensure unique slug (with max iterations to prevent infinite loop)
    base_slug = slug
    counter = 1
    max_attempts = 100  # SECURITY: Reduced from 1000 to prevent DoS

    while counter <= max_attempts:
        result = await db.execute(select(BlogPost).where(BlogPost.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    if counter > max_attempts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to generate unique slug - try a different title",
        )

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = [
        "title",
        "content",
        "excerpt",
        "featured_image",
        "category",
        "tags",
        "seo_title",
        "seo_description",
        "seo_keywords",
    ]
    post_data = {k: v for k, v in data.model_dump().items() if k in allowed_fields}

    post = BlogPost(
        author_id=current_user.id,
        slug=slug,
        status=BlogPostStatus.DRAFT,  # Always start as draft
        views_count=0,  # Initialize to 0
        **post_data,
    )
    db.add(post)
    await db.flush()
    await db.commit()

    # Invalidate blog caches
    await cache.invalidate_tag("blog")

    return BlogPostResponse.model_validate(post)


@router.put(
    "/{post_id}",
    response_model=BlogPostResponse,
    summary="Update blog post",
    description="Updates a blog post. SUPER_ADMIN role required. Rate limited to 30/minute. Logs blocked mass-assignment attempts.",
)
@limiter.limit("30/minute")  # Rate limiting: 30 updates por minuto
async def update_blog_post(
    request: Request,
    post_id: uuid.UUID,
    data: BlogPostUpdate,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found"
        )

    # SECURITY: Prevent mass assignment - only allow specific updatable fields
    allowed_fields = {
        "title",
        "content",
        "excerpt",
        "featured_image",
        "category",
        "tags",
        "seo_title",
        "seo_description",
        "seo_keywords",
        "status",
    }

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(post, field, value)
        else:
            # Log attempted mass assignment
            logger = get_logger(__name__)
            logger.warning(
                f"Mass assignment attempt blocked: field='{field}' user={current_user.id}"
            )

    await db.flush()
    await db.commit()

    # Invalidate caches for this post
    await cache.invalidate_tag(f"blog:{post_id}")
    await cache.invalidate_tag("blog")

    return BlogPostResponse.model_validate(post)


@router.delete(
    "/{post_id}",
    response_model=DeleteResponse,
    summary="Archive blog post",
    description="Archives (soft-deletes) a blog post by setting status to ARCHIVED. SUPER_ADMIN or ADMIN role required.",
)
async def delete_blog_post(
    post_id: uuid.UUID,
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(BlogPost).where(BlogPost.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found"
        )

    post.status = BlogPostStatus.ARCHIVED
    await db.flush()
    await db.commit()

    # Invalidate blog caches
    await cache.invalidate_tag(f"blog:{post_id}")
    await cache.invalidate_tag("blog")

    return {"message": "Blog post archived"}


@router.get(
    "/categories",
    response_model=BlogCategoriesResponse,
    summary="List blog categories",
    description="Returns a distinct list of categories from published blog posts.",
)
async def get_blog_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BlogPost.category)
        .where(BlogPost.status == BlogPostStatus.PUBLISHED)
        .distinct()
    )
    categories = [r[0] for r in result.all() if r[0]]
    return {"categories": categories}
