from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StaticPageBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    template: str | None = None
    meta_title: str | None = Field(None, max_length=70)
    meta_description: str | None = Field(None, max_length=160)
    is_active: bool = True
    show_in_footer: bool = False
    show_in_header: bool = False
    sort_order: int = 0


class StaticPageCreate(StaticPageBase):
    pass


class StaticPageUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(None, min_length=1, max_length=200)
    slug: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = None
    template: str | None = None
    meta_title: str | None = Field(None, max_length=70)
    meta_description: str | None = Field(None, max_length=160)
    is_active: bool | None = None
    show_in_footer: bool | None = None
    show_in_header: bool | None = None
    sort_order: int | None = None


class StaticPageResponse(StaticPageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class SEOSettingsBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_title_template: str = "{page_title} | {site_name}"
    default_meta_title: str = "Costa Rica Travel - Tours, Hotels & Vacation Packages"
    default_meta_description: str = (
        "Discover the best of Costa Rica with our curated tours, hotels, and vacation packages."
    )
    default_meta_keywords: list[str] = ["costa rica", "travel", "tours", "hotels"]
    google_site_verification: str | None = None
    robots_txt: str = "User-agent: *\nDisallow: /admin/\nDisallow: /superadmin/"
    sitemap_enabled: bool = True
    structured_data_enabled: bool = True


class SEOSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    site_title_template: str | None = None
    default_meta_title: str | None = None
    default_meta_description: str | None = None
    default_meta_keywords: list[str] | None = None
    google_site_verification: str | None = None
    robots_txt: str | None = None
    sitemap_enabled: bool | None = None
    structured_data_enabled: bool | None = None


class SEOSettingsResponse(SEOSettingsBase):
    id: UUID
    updated_by: UUID | None = None
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
    thumbnail_url: str | None = None
    alt_text: str | None = None
    folder: str | None = None


class MediaFileCreate(MediaFileBase):
    pass


class MediaFileResponse(MediaFileBase):
    id: UUID
    size_formatted: str = ""
    uploaded_by: str | None = None
    created_at: datetime
    used_in: list[str] = []

    model_config = ConfigDict(from_attributes=True, extra="forbid")
