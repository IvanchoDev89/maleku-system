from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class StaticPageBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    template: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    is_active: bool = True
    show_in_footer: bool = False
    show_in_header: bool = False
    sort_order: int = 0


class StaticPageCreate(StaticPageBase):
    pass


class StaticPageUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    template: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=70)
    meta_description: Optional[str] = Field(None, max_length=160)
    is_active: Optional[bool] = None
    show_in_footer: Optional[bool] = None
    show_in_header: Optional[bool] = None
    sort_order: Optional[int] = None


class StaticPageResponse(StaticPageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class SEOSettingsBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_title_template: str = "{page_title} | {site_name}"
    default_meta_title: str = "Costa Rica Travel - Tours, Hotels & Vacation Packages"
    default_meta_description: str = "Discover the best of Costa Rica with our curated tours, hotels, and vacation packages."
    default_meta_keywords: List[str] = ["costa rica", "travel", "tours", "hotels"]
    google_site_verification: Optional[str] = None
    robots_txt: str = "User-agent: *\nDisallow: /admin/\nDisallow: /superadmin/"
    sitemap_enabled: bool = True
    structured_data_enabled: bool = True


class SEOSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_title_template: Optional[str] = None
    default_meta_title: Optional[str] = None
    default_meta_description: Optional[str] = None
    default_meta_keywords: Optional[List[str]] = None
    google_site_verification: Optional[str] = None
    robots_txt: Optional[str] = None
    sitemap_enabled: Optional[bool] = None
    structured_data_enabled: Optional[bool] = None


class SEOSettingsResponse(SEOSettingsBase):
    id: UUID
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MediaFileBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    folder: Optional[str] = None


class MediaFileCreate(MediaFileBase):
    pass


class MediaFileResponse(MediaFileBase):
    id: UUID
    size_formatted: str = ""
    uploaded_by: Optional[str] = None
    created_at: datetime
    used_in: List[str] = []

    model_config = ConfigDict(from_attributes=True, extra="forbid")
