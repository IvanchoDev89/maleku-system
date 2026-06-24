"""
Tests for booking endpoints with real pricing logic
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession):
    """Create authenticated client with verified email"""
    from app.models import User, UserRole
    from app.core.security import get_password_hash, create_access_token

    user = User(
        email="client-booking@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Client Booking",
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=str(user.id))
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def vendor_entities(db_session: AsyncSession):
    """Create a vendor, property, room, and tour directly in DB. Return IDs."""
    from app.models import User, UserRole, Vendor, Property, Room
    from app.models.tour import Tour, TourCategory, TourDifficulty
    from app.core.security import get_password_hash

    user = User(
        email="vendor-booking@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Vendor Booking",
        role=UserRole.VENDOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    vendor = Vendor(
        user_id=user.id,
        business_name="Test Hotel Booking",
        business_slug=f"test-hotel-booking-{uuid.uuid4().hex[:8]}",
        business_type="hotel",
        is_active=True,
    )
    db_session.add(vendor)
    await db_session.flush()

    property_obj = Property(
        vendor_id=vendor.id,
        name="Test Property Booking",
        slug=f"test-property-booking-{uuid.uuid4().hex[:8]}",
        description="A test property",
        property_type="hotel",
        base_price=150.0,
        currency="USD",
        max_guests=4,
        is_active=True,
    )
    db_session.add(property_obj)
    await db_session.flush()

    room = Room(
        property_id=property_obj.id,
        name="Test Room",
        max_guests=2,
        price_per_night=150.0,
        weekend_price=180.0,
        is_available=True,
    )
    db_session.add(room)

    tour = Tour(
        vendor_id=vendor.id,
        name="Test Tour Booking",
        slug=f"test-tour-booking-{uuid.uuid4().hex[:8]}",
        description="A test tour",
        category=TourCategory.ADVENTURE.value,
        difficulty=TourDifficulty.EASY.value,
        duration_hours=4,
        price=75.0,
        location="Test Location",
        max_group_size=10,
        is_active=True,
    )
    db_session.add(tour)
    await db_session.commit()

    return {
        "property_id": str(property_obj.id),
        "room_id": str(room.id),
        "tour_id": str(tour.id),
        "vendor_id": str(vendor.id),
    }


@pytest.mark.asyncio
async def test_create_property_booking_without_room(
    auth_client: AsyncClient, vendor_entities
):
    """Test booking fails without room_id"""
    booking_data = {
        "property_id": vendor_entities["property_id"],
        "check_in": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "guests": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com",
        "guest_phone": "+50612345678",
    }

    response = await auth_client.post("/api/v1/bookings/property", json=booking_data)
    assert response.status_code == 400
    assert "room_id is required" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_property_booking_past_date(
    auth_client: AsyncClient, vendor_entities
):
    """Test booking fails with past check-in date"""
    booking_data = {
        "property_id": vendor_entities["property_id"],
        "room_id": vendor_entities["room_id"],
        "check_in": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "guests": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com",
    }

    response = await auth_client.post("/api/v1/bookings/property", json=booking_data)
    assert response.status_code == 400
    assert "cannot be in the past" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_property_booking_min_one_night(
    auth_client: AsyncClient, vendor_entities
):
    """Test booking requires minimum 1 night"""
    booking_data = {
        "property_id": vendor_entities["property_id"],
        "room_id": vendor_entities["room_id"],
        "check_in": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "guests": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com",
    }

    response = await auth_client.post("/api/v1/bookings/property", json=booking_data)
    assert response.status_code == 400
    assert "minimum stay" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_tour_booking_past_date(auth_client: AsyncClient, vendor_entities):
    """Test tour booking fails with past date"""
    booking_data = {
        "tour_id": vendor_entities["tour_id"],
        "booking_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "participants": 2,
        "guest_name": "Test Guest",
        "guest_email": "guest@example.com",
    }

    response = await auth_client.post("/api/v1/bookings/tour", json=booking_data)
    assert response.status_code == 400
    assert "cannot be in the past" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_price_preview_invalid_dates(auth_client: AsyncClient, vendor_entities):
    """Test price preview with invalid dates (check-out before check-in)"""
    preview_data = {
        "room_id": vendor_entities["room_id"],
        "check_in": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
        "check_out": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
        "guests": 2,
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
    response = await auth_client.get(
        "/api/v1/bookings/123e4567-e89b-12d3-a456-426614174000"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_booking_status_unauthorized(auth_client: AsyncClient):
    """Test updating booking status as client returns 403 (no update permission)"""
    response = await auth_client.put(
        "/api/v1/bookings/123e4567-e89b-12d3-a456-426614174000/status",
        json={"status": "confirmed"},
    )
    assert response.status_code == 403
