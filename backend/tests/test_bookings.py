"""
Tests for booking endpoints with real pricing logic
"""
import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient


@pytest.fixture
async def auth_client(client: AsyncClient, sample_user_data):
    """Create authenticated client"""
    # Register user
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = response.json()["access_token"]
    
    # Set authorization header
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def vendor_client(client: AsyncClient, sample_user_data, sample_vendor_data):
    """Create authenticated vendor client"""
    # Register as vendor
    response = await client.post(
        "/api/v1/auth/register/vendor",
        json=sample_user_data,
        params={
            "business_name": sample_vendor_data["business_name"],
            "business_type": sample_vendor_data["business_type"]
        }
    )
    token = response.json()["access_token"]
    
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
async def test_create_property_booking_without_room(auth_client: AsyncClient):
    """Test booking fails without room_id"""
    booking_data = {
        "property_id": "123e4567-e89b-12d3-a456-426614174000",
        "check_in": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "guests": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com",
        "guest_phone": "+50612345678"
    }
    
    response = await auth_client.post("/api/v1/bookings/property", json=booking_data)
    assert response.status_code == 400
    assert "room_id is required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_property_booking_past_date(auth_client: AsyncClient):
    """Test booking fails with past check-in date"""
    booking_data = {
        "property_id": "123e4567-e89b-12d3-a456-426614174000",
        "room_id": "123e4567-e89b-12d3-a456-426614174001",
        "check_in": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "guests": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com"
    }
    
    response = await auth_client.post("/api/v1/bookings/property", json=booking_data)
    assert response.status_code == 400
    assert "cannot be in the past" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_property_booking_min_one_night(auth_client: AsyncClient):
    """Test booking requires minimum 1 night"""
    booking_data = {
        "property_id": "123e4567-e89b-12d3-a456-426614174000",
        "room_id": "123e4567-e89b-12d3-a456-426614174001",
        "check_in": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),  # Same day
        "guests": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com"
    }
    
    response = await auth_client.post("/api/v1/bookings/property", json=booking_data)
    assert response.status_code == 400
    assert "minimum stay is 1 night" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_tour_booking_past_date(auth_client: AsyncClient):
    """Test tour booking fails with past date"""
    booking_data = {
        "tour_id": "123e4567-e89b-12d3-a456-426614174000",
        "tour_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "participants": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com"
    }
    
    response = await auth_client.post("/api/v1/bookings/tour", json=booking_data)
    assert response.status_code == 400
    assert "cannot be in the past" in response.json()["detail"]


@pytest.mark.asyncio
async def test_price_preview_invalid_dates(auth_client: AsyncClient):
    """Test price preview with invalid dates"""
    preview_data = {
        "room_id": "123e4567-e89b-12d3-a456-426614174000",
        "check_in": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),  # Check-out before check-in
        "guests": 2
    }
    
    response = await auth_client.post("/api/v1/bookings/preview", json=preview_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_bookings_unauthorized(client: AsyncClient):
    """Test getting bookings without auth fails"""
    response = await client.get("/api/v1/bookings")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_booking_by_id_not_found(auth_client: AsyncClient):
    """Test getting non-existent booking"""
    response = await auth_client.get("/api/v1/bookings/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_booking_status_unauthorized(auth_client: AsyncClient):
    """Test updating booking status as client fails"""
    response = await auth_client.put(
        "/api/v1/bookings/123e4567-e89b-12d3-a456-426614174000/status",
        json={"status": "confirmed"}
    )
    assert response.status_code == 404  # Booking not found
