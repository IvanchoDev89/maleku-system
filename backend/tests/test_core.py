import pytest
from datetime import timedelta
from uuid import uuid4


# Test config - run without async
# pytest_plugins = ('pytest_asyncio',)


# Sample data
@pytest.fixture
def sample_user():
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "phone": "+50612345678",
    }


@pytest.fixture
def sample_vendor():
    return {
        "business_name": "Test Hotel",
        "business_type": "hotel",
        "description": "A test hotel",
    }


@pytest.fixture
def sample_property():
    return {
        "vendor_id": uuid4(),
        "name": "Test Property",
        "slug": "test-property",
        "property_type": "hotel",
        "address": "Test Address",
        "country": "Costa Rica",
    }


# Validation tests
def test_sanitize_sql_injection():
    from app.schemas import is_dangerous_sql

    assert not is_dangerous_sql("Hello World")
    assert is_dangerous_sql("DROP TABLE users")
    assert is_dangerous_sql("DELETE FROM users")
    assert is_dangerous_sql("'; DROP TABLE --")


def test_password_strength():
    from app.schemas import is_weak_password

    assert is_weak_password("weak")
    assert is_weak_password("12345678")
    assert is_weak_password("ABCDEFGH")
    assert not is_weak_password("StrongPass123!")


# Schema tests
def test_schema_user_create(sample_user):
    from app.schemas import UserCreate

    user = UserCreate(**sample_user)
    assert user.email == sample_user["email"]
    assert user.full_name == sample_user["full_name"]


def test_schema_user_password_too_short():
    from app.schemas import UserCreate
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", password="short", full_name="Test User")


def test_schema_pagination():
    from app.schemas import PaginationParams

    params = PaginationParams(page=1, page_size=20)
    assert params.page == 1
    assert params.page_size == 20


def test_schema_vendor_create(sample_vendor):
    from app.schemas import VendorCreate

    vendor = VendorCreate(**sample_vendor)
    assert vendor.business_name == sample_vendor["business_name"]
    assert vendor.business_type == sample_vendor["business_type"]


# Authentication tests
def test_password_hashing():
    from app.core.security import get_password_hash, verify_password

    password = "TestPass123"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed)
    assert not verify_password("WrongPass", hashed)


def test_jwt_token_creation():
    from app.core.security import (
        create_access_token,
        create_refresh_token,
        decode_token,
    )

    user_id = str(uuid4())
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    assert access_token
    assert refresh_token

    payload = decode_token(access_token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_token_expiration():
    from app.core.security import create_access_token, decode_token
    from fastapi import HTTPException

    user_id = str(uuid4())
    expired_token = create_access_token(user_id, expires_delta=timedelta(seconds=-1))

    with pytest.raises(HTTPException):
        decode_token(expired_token)


# Model tests
def test_user_model_fields():
    from app.models import User

    required_fields = ["id", "email", "password_hash", "full_name", "role", "is_active"]
    for field in required_fields:
        assert hasattr(User, field), f"User missing {field}"


def test_vendor_model_fields():
    from app.models import Vendor

    required_fields = ["id", "user_id", "business_name", "business_slug", "is_active"]
    for field in required_fields:
        assert hasattr(Vendor, field), f"Vendor missing {field}"


def test_property_model():
    from app.models import Property

    assert hasattr(Property, "vendor_id")
    assert hasattr(Property, "slug")


def test_booking_status_enum():
    from app.models import BookingStatus

    assert BookingStatus.PENDING.value == "pending"
    assert BookingStatus.CONFIRMED.value == "confirmed"
    assert BookingStatus.CANCELLED.value == "cancelled"
    assert BookingStatus.COMPLETED.value == "completed"


def test_tour_category_enum():
    from app.models import TourCategory

    assert TourCategory.ADVENTURE.value == "adventure"
    assert TourCategory.NATURE.value == "nature"


# CRUD tests
def test_crud_base_import():
    from app.crud import CRUDBase, CRUDUser, CRUDSlug, CRUDRating

    assert CRUDBase
    assert CRUDUser
    assert CRUDSlug
    assert CRUDRating


# Service tests - verify actual services used in the application
def test_cache_service_import():
    from app.services.cache_service import CacheService, cache

    assert CacheService
    assert cache


def test_pricing_service_import():
    from app.services.pricing_service import calculate_room_price, calculate_tour_price

    assert calculate_room_price
    assert calculate_tour_price


# Exception tests
def test_exceptions_import():
    from app.exceptions import NotFoundException, AlreadyExistsException

    assert NotFoundException
    assert AlreadyExistsException


def test_not_found_exception():
    from app.exceptions import NotFoundException
    from fastapi import status

    exc = NotFoundException("User", "123")
    assert "not found" in exc.message
    assert exc.status_code == status.HTTP_404_NOT_FOUND


# Configuration tests
def test_config_import():
    from app.core.config import settings

    assert settings.APP_NAME == "Costa Rica Travel"
    assert settings.SECRET_KEY


# Pagination tests
def test_pagination_params_defaults():
    from app.schemas import PaginationParams

    params = PaginationParams(page=1, page_size=20)
    assert params.page == 1
    assert params.page_size == 20
    assert params.offset == 0


def test_pagination_params_offset():
    from app.schemas import PaginationParams

    params = PaginationParams(page=3, page_size=10)
    assert params.offset == 20


def test_pagination_metadata():
    from app.core.pagination import PaginationMetadata

    meta = PaginationMetadata(
        page=2, page_size=10, total=25, total_pages=3, has_next=True, has_prev=True
    )
    assert meta.page == 2
    assert meta.total == 25
    assert meta.total_pages == 3
    assert meta.has_next is True
    assert meta.has_prev is True


def test_pagination_metadata_last_page():
    from app.core.pagination import PaginationMetadata

    meta = PaginationMetadata(
        page=3, page_size=10, total=25, total_pages=3, has_next=False, has_prev=True
    )
    assert meta.has_next is False
    assert meta.has_prev is True


def test_paginated_result():
    from app.core.pagination import PaginatedResult, PaginationMetadata

    meta = PaginationMetadata(
        page=1, page_size=10, total=3, total_pages=1, has_next=False, has_prev=False
    )
    result = PaginatedResult(items=["a", "b", "c"], pagination=meta)
    assert len(result.items) == 3
    assert result.items == ["a", "b", "c"]
    assert result.pagination.total == 3


@pytest.mark.asyncio
async def test_paginate_list():
    from app.core.pagination import paginate_list, PaginationParams

    items = list(range(50))
    params = PaginationParams(page=2, page_size=10)

    result = await paginate_list(items, params)
    assert len(result.items) == 10
    assert result.items[0] == 10
    assert result.items[-1] == 19
    assert result.pagination.total == 50
    assert result.pagination.total_pages == 5
    assert result.pagination.has_next is True
    assert result.pagination.has_prev is True


@pytest.mark.asyncio
async def test_paginate_list_last_page():
    from app.core.pagination import paginate_list, PaginationParams

    items = list(range(25))
    params = PaginationParams(page=3, page_size=10)

    result = await paginate_list(items, params)
    assert len(result.items) == 5
    assert result.items[0] == 20
    assert result.items[-1] == 24
    assert result.pagination.has_next is False
    assert result.pagination.has_prev is True


@pytest.mark.asyncio
async def test_paginate_list_empty():
    from app.core.pagination import paginate_list, PaginationParams

    result = await paginate_list([], PaginationParams(page=1, page_size=20))
    assert len(result.items) == 0
    assert result.pagination.total == 0
    assert result.pagination.total_pages == 0
    assert result.pagination.has_next is False
    assert result.pagination.has_prev is False


def test_paginate_flat_dict_shape():
    from app.core.pagination import paginate_flat

    import inspect

    sig = inspect.signature(paginate_flat)
    params = list(sig.parameters.keys())
    assert "session" in params
    assert "query" in params
    assert "params" in params
    assert "transform_func" in params
    assert "order_by" in params


def test_pagination_imports():
    from app.core.pagination import (
        PaginationMetadata,
        PaginatedResult,
        paginate_query,
        paginate_list,
        paginate_flat,
    )
    from app.schemas import PaginationParams

    assert PaginationParams
    assert PaginationMetadata
    assert PaginatedResult
    assert paginate_query
    assert paginate_list
    assert paginate_flat


# Run with: pytest -v
# or: python -m pytest -v
