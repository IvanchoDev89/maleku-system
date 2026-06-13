"""
Super Admin Content Management API

Manages blog posts, static pages, SEO settings, and media library.
Exclusive access for SUPER_ADMIN role.
"""

from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_superadmin
from app.models import User
from app.services.audit_service import AuditService
from app.models.audit import AuditAction

router = APIRouter(prefix="/content", tags=["Super Admin - Content"])


def _serialize_for_audit(data: dict) -> dict:
    """Convert non-JSON-serializable values (datetime, etc.) to strings."""
    result = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif hasattr(v, "isoformat"):
            result[k] = str(v)
        else:
            result[k] = v
    return result


class ContentStatus(str, Enum):
    draft = "draft"
    published = "published"
    scheduled = "scheduled"
    archived = "archived"


class BlogPost(BaseModel):
    """Blog post model"""

    id: str
    title: str
    slug: str
    excerpt: str
    content: str
    featured_image: Optional[str]
    author: str
    author_id: str
    status: ContentStatus
    tags: List[str]
    meta_title: str
    meta_description: str
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    views: int


class BlogPostCreate(BaseModel):
    """Create blog post"""

    title: str = Field(..., min_length=5, max_length=200)
    excerpt: str = Field(..., max_length=500)
    content: str = Field(..., min_length=50)
    featured_image: Optional[str] = None
    status: ContentStatus = ContentStatus.draft
    tags: List[str] = []
    meta_title: str = Field("", max_length=70)
    meta_description: str = Field("", max_length=160)
    published_at: Optional[datetime] = None


class BlogPostUpdate(BaseModel):
    """Update blog post"""

    title: Optional[str] = Field(None, min_length=5, max_length=200)
    excerpt: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = Field(None, min_length=50)
    featured_image: Optional[str] = None
    status: Optional[ContentStatus] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    published_at: Optional[datetime] = None


class StaticPage(BaseModel):
    """Static page model"""

    id: str
    title: str
    slug: str
    content: str
    template: str
    meta_title: str
    meta_description: str
    is_active: bool
    show_in_footer: bool
    show_in_header: bool
    sort_order: int
    updated_at: datetime


class StaticPageUpdate(BaseModel):
    """Update static page"""

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    is_active: Optional[bool] = None
    show_in_footer: Optional[bool] = None
    show_in_header: Optional[bool] = None


class SEOSettings(BaseModel):
    """Global SEO settings"""

    site_title_template: str = "{page_title} | {site_name}"
    default_meta_title: str = "Costa Rica Travel - Tours, Hotels & Vacation Packages"
    default_meta_description: str = "Discover the best of Costa Rica with our curated tours, hotels, and vacation packages."
    default_meta_keywords: List[str] = ["costa rica", "travel", "tours", "hotels"]
    google_site_verification: str = ""
    robots_txt: str = "User-agent: *\nDisallow: /admin/\nDisallow: /superadmin/"
    sitemap_enabled: bool = True
    structured_data_enabled: bool = True


class MediaFile(BaseModel):
    """Media file model"""

    id: str
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    size_formatted: str
    url: str
    thumbnail_url: Optional[str]
    alt_text: str
    folder: str
    uploaded_by: str
    uploaded_at: datetime
    used_in: List[str]  # Pages where this media is used


# Mock data stores (replace with database in production)
_blog_posts = [
    {
        "id": "bp-001",
        "title": "10 Best Beaches in Costa Rica",
        "slug": "10-best-beaches-costa-rica",
        "excerpt": "Discover the most beautiful beaches in Costa Rica...",
        "content": "<p>Costa Rica is home to some of the world's most beautiful beaches...</p>",
        "featured_image": "https://example.com/beach.jpg",
        "author": "Travel Expert",
        "author_id": "user-001",
        "status": "published",
        "tags": ["beaches", "travel tips", "manuel antonio"],
        "meta_title": "10 Best Beaches in Costa Rica | Costa Rica Travel",
        "meta_description": "Discover the most beautiful beaches in Costa Rica. From Manuel Antonio to Tamarindo.",
        "published_at": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        "created_at": datetime(2024, 1, 10, 8, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        "views": 1250,
    },
    {
        "id": "bp-002",
        "title": "Guide to Arenal Volcano",
        "slug": "guide-arenal-volcano",
        "excerpt": "Everything you need to know about visiting Arenal...",
        "content": "<p>The Arenal Volcano is one of Costa Rica's most iconic landmarks...</p>",
        "featured_image": "https://example.com/volcano.jpg",
        "author": "Adventure Guide",
        "author_id": "user-002",
        "status": "draft",
        "tags": ["volcano", "adventure", "la fortuna"],
        "meta_title": "",
        "meta_description": "",
        "published_at": None,
        "created_at": datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc),
        "views": 0,
    },
]

_static_pages = [
    {
        "id": "page-about",
        "title": "About Us",
        "slug": "about",
        "content": "<p>We are Costa Rica Travel...</p>",
        "template": "default",
        "meta_title": "About Costa Rica Travel",
        "meta_description": "Learn about our company and mission.",
        "is_active": True,
        "show_in_footer": True,
        "show_in_header": False,
        "sort_order": 1,
        "updated_at": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    },
    {
        "id": "page-contact",
        "title": "Contact Us",
        "slug": "contact",
        "content": "<p>Get in touch with us...</p>",
        "template": "contact",
        "meta_title": "Contact Costa Rica Travel",
        "meta_description": "Contact us for bookings and inquiries.",
        "is_active": True,
        "show_in_footer": True,
        "show_in_header": True,
        "sort_order": 2,
        "updated_at": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    },
    {
        "id": "page-terms",
        "title": "Terms of Service",
        "slug": "terms",
        "content": "<p>Terms and conditions...</p>",
        "template": "default",
        "meta_title": "Terms of Service",
        "meta_description": "Our terms and conditions.",
        "is_active": True,
        "show_in_footer": True,
        "show_in_header": False,
        "sort_order": 3,
        "updated_at": datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    },
]

_seo_settings = SEOSettings()

_media_files = [
    {
        "id": "media-001",
        "filename": "beach-sunset.jpg",
        "original_name": "DSC001.jpg",
        "mime_type": "image/jpeg",
        "size_bytes": 2457600,
        "size_formatted": "2.3 MB",
        "url": "https://example.com/media/beach-sunset.jpg",
        "thumbnail_url": "https://example.com/media/thumbs/beach-sunset.jpg",
        "alt_text": "Beautiful sunset at Costa Rican beach",
        "folder": "destinations",
        "uploaded_by": "admin@example.com",
        "uploaded_at": datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
        "used_in": ["bp-001", "page-about"],
    },
    {
        "id": "media-002",
        "filename": "volcano-tour.mp4",
        "original_name": "tour-video.mp4",
        "mime_type": "video/mp4",
        "size_bytes": 52428800,
        "size_formatted": "50 MB",
        "url": "https://example.com/media/volcano-tour.mp4",
        "thumbnail_url": "https://example.com/media/thumbs/volcano-tour.jpg",
        "alt_text": "Arenal Volcano Tour Video",
        "folder": "videos",
        "uploaded_by": "admin@example.com",
        "uploaded_at": datetime(2024, 2, 1, 9, 0, 0, tzinfo=timezone.utc),
        "used_in": [],
    },
]


@router.get("/blog", response_model=List[BlogPost])
async def list_blog_posts(
    status_filter: Optional[ContentStatus] = Query(None, alias="status"),
    tag: Optional[str] = Query(None, max_length=50),
    author_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """List all blog posts with filtering"""
    posts = _blog_posts

    if status_filter:
        posts = [p for p in posts if p["status"] == status_filter]
    if tag:
        posts = [p for p in posts if tag in p["tags"]]
    if author_id:
        posts = [p for p in posts if p["author_id"] == author_id]
    if search:
        posts = [p for p in posts if search.lower() in p["title"].lower()]

    return [BlogPost(**p) for p in posts[offset : offset + limit]]


@router.get("/blog/{post_id}", response_model=BlogPost)
async def get_blog_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get single blog post"""
    post = next((p for p in _blog_posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return BlogPost(**post)


@router.post("/blog", response_model=BlogPost, status_code=201)
async def create_blog_post(
    data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Create new blog post"""
    new_id = f"bp-{len(_blog_posts) + 1:03d}"

    post = {
        "id": new_id,
        "title": data.title,
        "slug": data.title.lower().replace(" ", "-"),
        "excerpt": data.excerpt,
        "content": data.content,
        "featured_image": data.featured_image,
        "author": current_user.full_name or current_user.email,
        "author_id": str(current_user.id),
        "status": data.status,
        "tags": data.tags,
        "meta_title": data.meta_title or data.title,
        "meta_description": data.meta_description or data.excerpt[:160],
        "published_at": data.published_at,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "views": 0,
    }

    _blog_posts.insert(0, post)

    # Log action
    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.CREATE,
        entity_type="blog_post",
        entity_id=None,
        new_values=_serialize_for_audit(post),
        changes_summary=f"Blog post '{data.title}' created",
    )

    return BlogPost(**post)


@router.put("/blog/{post_id}", response_model=BlogPost)
async def update_blog_post(
    post_id: str,
    data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update blog post"""
    post = next((p for p in _blog_posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    old_values = {
        k: v for k, v in post.items() if k in data.model_dump(exclude_unset=True)
    }

    # SECURITY: Prevent mass assignment - only allow fields defined in BlogPostUpdate
    allowed_fields = {
        "title",
        "excerpt",
        "content",
        "featured_image",
        "status",
        "tags",
        "meta_title",
        "meta_description",
        "published_at",
    }

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            post[key] = value

    post["updated_at"] = datetime.now(timezone.utc)

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="blog_post",
        entity_id=None,
        old_values=_serialize_for_audit(old_values),
        new_values=_serialize_for_audit(post),
        changes_summary=f"Blog post '{post['title']}' updated",
    )

    return BlogPost(**post)


@router.delete("/blog/{post_id}", response_model=dict, status_code=200)
async def delete_blog_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Delete blog post"""
    post = next((p for p in _blog_posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    _blog_posts.remove(post)

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="blog_post",
        entity_id=None,
        old_values=_serialize_for_audit(post),
        changes_summary=f"Blog post '{post['title']}' deleted",
    )

    return None


@router.get("/pages", response_model=List[StaticPage])
async def list_static_pages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """List all static pages"""
    return [StaticPage(**p) for p in _static_pages]


@router.get("/pages/{page_id}", response_model=StaticPage)
async def get_static_page(
    page_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get single static page"""
    page = next((p for p in _static_pages if p["id"] == page_id), None)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return StaticPage(**page)


@router.put("/pages/{page_id}", response_model=StaticPage)
async def update_static_page(
    page_id: str,
    data: StaticPageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update static page"""
    page = next((p for p in _static_pages if p["id"] == page_id), None)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    old_values = {
        k: v for k, v in page.items() if k in data.model_dump(exclude_unset=True)
    }

    # SECURITY: Prevent mass assignment - only allow fields defined in StaticPageUpdate
    allowed_fields = {"title", "content", "meta_title", "meta_description"}

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            page[key] = value

    page["updated_at"] = datetime.now(timezone.utc)

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="static_page",
        entity_id=None,
        old_values=_serialize_for_audit(old_values),
        new_values=_serialize_for_audit(page),
        changes_summary=f"Static page '{page['title']}' updated",
    )

    return StaticPage(**page)


@router.get("/seo", response_model=SEOSettings)
async def get_seo_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get global SEO settings"""
    return _seo_settings


@router.put("/seo", response_model=SEOSettings)
async def update_seo_settings(
    data: SEOSettings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update global SEO settings"""
    global _seo_settings

    old_values = _seo_settings.model_dump()

    _seo_settings = data

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="seo_settings",
        entity_id=None,
        old_values=_serialize_for_audit(old_values),
        new_values=_serialize_for_audit(data.model_dump()),
        changes_summary="SEO settings updated",
    )

    return _seo_settings


@router.get("/media", response_model=List[MediaFile])
async def list_media(
    folder: Optional[str] = Query(None, max_length=50),
    mime_type: Optional[str] = Query(None, max_length=50),
    search: Optional[str] = Query(None, max_length=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """List media files"""
    media = _media_files

    if folder:
        media = [m for m in media if m["folder"] == folder]
    if mime_type:
        media = [m for m in media if m["mime_type"].startswith(mime_type)]
    if search:
        media = [m for m in media if search.lower() in m["filename"].lower()]

    return [MediaFile(**m) for m in media[offset : offset + limit]]


@router.delete("/media/{media_id}", response_model=dict, status_code=200)
async def delete_media(
    media_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Delete media file"""
    media = next((m for m in _media_files if m["id"] == media_id), None)
    if not media:
        raise HTTPException(status_code=404, detail="Media file not found")

    if media["used_in"]:
        raise HTTPException(
            status_code=400,
            detail=f"Media is used in {len(media['used_in'])} places. Remove references first.",
        )

    _media_files.remove(media)

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="media",
        entity_id=None,
        old_values=_serialize_for_audit(media),
        changes_summary=f"Media file '{media['filename']}' deleted",
    )

    return None
