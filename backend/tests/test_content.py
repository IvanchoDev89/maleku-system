"""
Unit tests for Content schemas
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone


class TestStaticPageSchemas:
    def test_static_page_create_valid(self):
        from app.schemas.content import StaticPageCreate, StaticPageResponse

        data = StaticPageCreate(
            title="About Us",
            slug="about",
            content="<p>About page content</p>",
            template="default",
            is_active=True,
            show_in_footer=True,
        )
        assert data.title == "About Us"
        assert data.slug == "about"
        assert data.is_active is True
        assert data.show_in_footer is True

        now = datetime.now(timezone.utc)
        response = StaticPageResponse(
            id=uuid4(),
            title=data.title,
            slug=data.slug,
            content=data.content,
            template=data.template,
            is_active=data.is_active,
            show_in_footer=data.show_in_footer,
            show_in_header=data.show_in_header,
            sort_order=data.sort_order,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            created_at=now,
            updated_at=now,
        )
        assert response.id is not None
        assert response.title == "About Us"

    def test_static_page_update_partial(self):
        from app.schemas.content import StaticPageUpdate

        data = StaticPageUpdate(title="Updated Title", is_active=False)
        assert data.title == "Updated Title"
        assert data.is_active is False
        assert data.content is None
        assert data.slug is None

    def test_static_page_update_empty(self):
        from app.schemas.content import StaticPageUpdate

        data = StaticPageUpdate()
        assert data.title is None

    def test_static_page_create_forbid_extra(self):
        from app.schemas.content import StaticPageCreate

        with pytest.raises(ValueError):
            StaticPageCreate(title="Test", slug="test", content="", malicious_field="hack")


class TestSEOSettingsSchemas:
    def test_seo_settings_defaults(self):
        from app.schemas.content import SEOSettingsBase, SEOSettingsResponse

        data = SEOSettingsBase()
        assert data.site_title_template == "{page_title} | {site_name}"
        assert data.sitemap_enabled is True
        assert "costa rica" in data.default_meta_keywords

        now = datetime.now(timezone.utc)
        response = SEOSettingsResponse(
            id=uuid4(),
            site_title_template=data.site_title_template,
            default_meta_title=data.default_meta_title,
            default_meta_description=data.default_meta_description,
            default_meta_keywords=data.default_meta_keywords,
            google_site_verification=data.google_site_verification,
            robots_txt=data.robots_txt,
            sitemap_enabled=data.sitemap_enabled,
            structured_data_enabled=data.structured_data_enabled,
            created_at=now,
            updated_at=now,
        )
        assert response.sitemap_enabled is True

    def test_seo_settings_update_partial(self):
        from app.schemas.content import SEOSettingsUpdate

        data = SEOSettingsUpdate(sitemap_enabled=False, robots_txt="Disallow: /")
        assert data.sitemap_enabled is False
        assert data.robots_txt == "Disallow: /"
        assert data.default_meta_title is None


class TestMediaFileSchemas:
    def test_media_file_create_valid(self):
        from app.schemas.content import MediaFileCreate, MediaFileResponse

        data = MediaFileCreate(
            filename="beach.jpg",
            original_name="DSC001.jpg",
            mime_type="image/jpeg",
            size_bytes=2457600,
            url="https://example.com/media/beach.jpg",
            folder="destinations",
        )
        assert data.filename == "beach.jpg"
        assert data.size_bytes == 2457600
        assert data.alt_text is None

        now = datetime.now(timezone.utc)
        response = MediaFileResponse(
            id=uuid4(),
            filename=data.filename,
            original_name=data.original_name,
            mime_type=data.mime_type,
            size_bytes=data.size_bytes,
            size_formatted="2.3 MB",
            url=data.url,
            thumbnail_url=data.thumbnail_url,
            alt_text=data.alt_text,
            folder=data.folder,
            uploaded_by="admin@example.com",
            created_at=now,
            used_in=[],
        )
        assert response.size_formatted == "2.3 MB"
        assert response.used_in == []


class TestContentImports:
    def test_content_model_import(self):
        from app.models.content import StaticPage, SEOSettings, MediaFile

        assert StaticPage
        assert SEOSettings
        assert MediaFile

    def test_content_schemas_import(self):
        from app.schemas.content import (
            StaticPageCreate,
            StaticPageUpdate,
            StaticPageResponse,
            SEOSettingsBase,
            SEOSettingsUpdate,
            SEOSettingsResponse,
            MediaFileCreate,
            MediaFileResponse,
        )

        assert StaticPageCreate
        assert StaticPageUpdate
        assert StaticPageResponse
        assert SEOSettingsBase
        assert SEOSettingsUpdate
        assert SEOSettingsResponse
        assert MediaFileCreate
        assert MediaFileResponse

    def test_content_router_import(self):
        from app.api.v1.superadmin.content import router

        assert router

    def test_content_models_in_all(self):
        from app.models import __all__ as model_all

        assert "StaticPage" in model_all
        assert "SEOSettings" in model_all
        assert "MediaFile" in model_all
