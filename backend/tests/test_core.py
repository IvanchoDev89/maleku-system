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
        "password": "TestPass123",
        "full_name": "Test User",
        "phone": "+50612345678"
    }


@pytest.fixture  
def sample_vendor():
    return {
        "user_id": uuid4(),
        "business_name": "Test Hotel",
        "business_type": "hotel",
        "description": "A test hotel"
    }


@pytest.fixture
def sample_property():
    return {
        "vendor_id": uuid4(),
        "name": "Test Property",
        "slug": "test-property",
        "property_type": "hotel",
        "address": "Test Address",
        "country": "Costa Rica"
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
    assert not is_weak_password("StrongPass123")


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
        UserCreate(
            email="test@example.com",
            password="short",
            full_name="Test User"
        )


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
    from app.core.security import create_access_token, create_refresh_token, decode_token
    
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
    from app.services.cache_service import CacheService, cache_service
    assert CacheService
    assert cache_service


def test_pricing_service_import():
    from app.services.pricing_service import calculate_room_price, calculate_tour_price
    assert calculate_room_price
    assert calculate_tour_price


# Exception tests  
def test_exceptions_import():
    from app.exceptions import (
        NotFoundException, AlreadyExistsException
    )
    
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


# Run with: pytest -v
# or: python -m pytest -v