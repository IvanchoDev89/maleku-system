"""
Unit tests for Blog schemas
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone


class TestBlogSchemas:
    def test_blog_post_create_valid(self):
        from app.schemas import BlogPostCreate

        data = BlogPostCreate(
            title="Valid Blog Post Title",
            content="A" * 50,
            category="Travel",
            tags=["costa-rica", "travel"],
        )
        assert data.title == "Valid Blog Post Title"
        assert len(data.content) == 50
        assert data.tags == ["costa-rica", "travel"]

    def test_blog_post_create_minimal(self):
        from app.schemas import BlogPostCreate

        data = BlogPostCreate(title="Minimal Post", content="X" * 50)
        assert data.title == "Minimal Post"
        assert data.excerpt is None
        assert data.featured_image is None
        assert data.tags is None

    def test_blog_post_create_title_too_short(self):
        from app.schemas import BlogPostCreate

        with pytest.raises(ValueError):
            BlogPostCreate(title="AB", content="X" * 50)

    def test_blog_post_create_content_too_short(self):
        from app.schemas import BlogPostCreate

        with pytest.raises(ValueError):
            BlogPostCreate(title="Valid Title", content="Short")

    def test_blog_post_update_partial(self):
        from app.schemas import BlogPostUpdate

        data = BlogPostUpdate(title="Revised Title")
        assert data.title == "Revised Title"
        assert data.excerpt is None
        assert data.content is None

    def test_blog_post_update_empty(self):
        from app.schemas import BlogPostUpdate

        data = BlogPostUpdate()
        assert data.title is None

    def test_blog_post_response(self):
        from app.schemas import BlogPostResponse

        now = datetime.now(timezone.utc)
        data = BlogPostResponse(
            id=uuid4(),
            title="Response Title",
            content="X" * 50,
            author_id=None,
            status="published",
            views_count=42,
            is_featured=True,
            published_at=None,
            created_at=now,
        )
        assert data.status == "published"
        assert data.views_count == 42
        assert data.is_featured is True

    def test_blog_post_list_response(self):
        from app.schemas import BlogPostListResponse

        data = BlogPostListResponse(
            id=uuid4(),
            title="List Item",
            excerpt="A brief excerpt",
            category="Travel",
            status="draft",
            views_count=0,
            is_featured=False,
        )
        assert data.status == "draft"
        assert data.is_featured is False


class TestBlogImports:
    def test_router_import(self):
        from app.api.v1.blog import router

        assert router

    def test_blog_schemas_import(self):
        from app.schemas import (
            BlogPostCreate,
            BlogPostUpdate,
            BlogPostResponse,
            BlogPostListResponse,
        )

        assert BlogPostCreate
        assert BlogPostUpdate
        assert BlogPostResponse
        assert BlogPostListResponse
