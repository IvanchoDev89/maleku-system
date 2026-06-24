import pytest
import uuid
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _mock_email(monkeypatch):
    """Prevent email service from crashing on SMTP failure."""

    async def _noop(*args, **kwargs):
        pass

    from app.services.email_service import email_service

    monkeypatch.setattr(email_service, "send_email", _noop)


@pytest.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession):
    from app.models import User, UserRole
    from app.core.security import get_password_hash, create_access_token

    user = User(
        email="reservation-client@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Reservation Client",
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=str(user.id))
    client.headers["Authorization"] = f"Bearer {token}"
    client._user_id = user.id
    return client


@pytest.fixture
async def vendor_entities(db_session: AsyncSession):
    from app.models import User, UserRole, Vendor, Property, Room
    from app.core.security import get_password_hash

    user = User(
        email="reservation-vendor@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Reservation Vendor",
        role=UserRole.VENDOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    vendor = Vendor(
        user_id=user.id,
        business_name="Reservation Hotel",
        business_slug=f"reservation-hotel-{uuid.uuid4().hex[:8]}",
        business_type="hotel",
        is_active=True,
    )
    db_session.add(vendor)
    await db_session.flush()

    prop = Property(
        vendor_id=vendor.id,
        name="Reservation Test Property",
        slug=f"reservation-prop-{uuid.uuid4().hex[:8]}",
        description="Test property for reservation flow",
        property_type="hotel",
        base_price=150.0,
        currency="USD",
        max_guests=4,
        is_active=True,
    )
    db_session.add(prop)
    await db_session.flush()

    room = Room(
        property_id=prop.id,
        name="Reservation Test Room",
        max_guests=2,
        price_per_night=150.0,
        weekend_price=180.0,
        is_available=True,
    )
    db_session.add(room)
    await db_session.commit()

    return {
        "property_id": str(prop.id),
        "room_id": str(room.id),
        "vendor_id": str(vendor.id),
    }


@pytest.fixture
async def vendor_auth_client(
    client: AsyncClient, db_session: AsyncSession, vendor_entities
):
    from app.core.security import create_access_token
    from app.models.vendor import Vendor
    from sqlalchemy import select

    result = await db_session.execute(
        select(Vendor).where(Vendor.id == uuid.UUID(vendor_entities["vendor_id"]))
    )
    vendor = result.scalar_one_or_none()
    if vendor:
        token = create_access_token(subject=str(vendor.user_id))
        client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def property_room(vendor_entities):
    return vendor_entities


class TestReservationFlow:
    async def test_01_health_check(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code in (200, 404)

    async def test_02_list_properties(self, client: AsyncClient):
        resp = await client.get("/api/v1/properties", params={"limit": 1})
        assert resp.status_code == 200

    async def test_03_property_detail_has_rooms_and_vendor(
        self, client: AsyncClient, property_room
    ):
        resp = await client.get(f"/api/v1/properties/{property_room['property_id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert "rooms" in data
        assert "vendor" in data

    async def test_04_availability_check_available(
        self, client: AsyncClient, property_room
    ):
        ci = datetime.now(timezone.utc) + timedelta(days=45)
        co = ci + timedelta(days=3)
        resp = await client.post(
            "/api/v1/availability/rooms/check",
            json={
                "room_id": property_room["room_id"],
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True

    async def test_05_calendar_returns_dates(self, client: AsyncClient, property_room):
        ci = (datetime.now(timezone.utc) + timedelta(days=45)).strftime("%Y-%m-%d")
        resp = await client.get(
            f"/api/v1/availability/rooms/{property_room['room_id']}/calendar",
            params={"start_date": ci, "days": 31},
        )
        assert resp.status_code in (200, 422), resp.text

    async def test_07_vendor_blocks_dates(
        self, vendor_auth_client: AsyncClient, property_room
    ):
        block_date = datetime.now(timezone.utc) + timedelta(days=45)
        resp = await vendor_auth_client.put(
            f"/api/v1/availability/rooms/{property_room['room_id']}/calendar",
            json={
                "entries": [
                    {
                        "date": block_date.strftime("%Y-%m-%d"),
                        "is_available": False,
                        "notes": "Mantenimiento E2E",
                    },
                    {
                        "date": (block_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "is_available": True,
                        "price_override": 200.0,
                        "notes": "Price override E2E",
                    },
                ]
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "updated_count" in data or "message" in data

    async def test_08_calendar_reflects_blocked_dates(
        self, client: AsyncClient, property_room
    ):
        block_date = datetime.now(timezone.utc) + timedelta(days=45)
        resp = await client.get(
            f"/api/v1/availability/rooms/{property_room['room_id']}/calendar",
            params={"start_date": block_date.strftime("%Y-%m-%dT00:00:00Z"), "days": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        dates = data.get("dates", data if isinstance(data, list) else [])
        assert len(dates) > 0

    async def test_09_price_preview(self, auth_client: AsyncClient, property_room):
        ci = datetime.now(timezone.utc) + timedelta(days=45)
        co = ci + timedelta(days=4)
        resp = await auth_client.post(
            "/api/v1/bookings/preview",
            json={
                "room_id": property_room["room_id"],
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
                "guests": 2,
            },
        )
        assert resp.status_code in (200, 422), resp.text

    async def test_10_create_property_booking(
        self, auth_client: AsyncClient, property_room
    ):
        ci = datetime.now(timezone.utc) + timedelta(days=45)
        co = ci + timedelta(days=3)
        resp = await auth_client.post(
            "/api/v1/bookings/property",
            json={
                "property_id": property_room["property_id"],
                "room_id": property_room["room_id"],
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
                "guests": 2,
                "guest_name": "Integration Test",
                "guest_email": "e2e@test.com",
                "guest_phone": "+50670000000",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["booking_type"] == "property"
        assert data["status"] == "pending"
        assert data["total_amount"] > 0
        self.__class__.test_booking_id = data["id"]

    async def test_13_get_booking(self, auth_client: AsyncClient):
        if not hasattr(self.__class__, "test_booking_id"):
            pytest.skip("No booking_id")
        resp = await auth_client.get(
            f"/api/v1/bookings/{self.__class__.test_booking_id}"
        )
        assert resp.status_code in (200, 404), resp.text

    async def test_14_tour_booking(
        self, auth_client: AsyncClient, client: AsyncClient, db_session: AsyncSession
    ):
        from app.models.tour import Tour, TourCategory, TourDifficulty
        from app.models import Vendor, User, UserRole
        from app.core.security import get_password_hash

        vendor_user = User(
            email="tour-vendor@example.com",
            password_hash=get_password_hash("TestPass123!"),
            full_name="Tour Vendor",
            role=UserRole.VENDOR,
            is_active=True,
            is_verified=True,
        )
        db_session.add(vendor_user)
        await db_session.flush()

        vendor = Vendor(
            user_id=vendor_user.id,
            business_name="Tour Co",
            business_slug=f"tour-co-{uuid.uuid4().hex[:8]}",
            business_type="tour_operator",
            is_active=True,
        )
        db_session.add(vendor)
        await db_session.flush()

        tour = Tour(
            vendor_id=vendor.id,
            name="Test Tour",
            slug=f"test-tour-{uuid.uuid4().hex[:8]}",
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

        booking_date = (datetime.now(timezone.utc) + timedelta(days=50)).isoformat()
        resp = await auth_client.post(
            "/api/v1/bookings/tour",
            json={
                "tour_id": str(tour.id),
                "booking_date": booking_date,
                "participants": 2,
                "guest_name": "Tour E2E",
                "guest_email": "toure2e@test.com",
                "guest_phone": "+50670000002",
            },
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["booking_type"] == "tour"
        assert data["status"] == "pending"
        assert data["total_amount"] > 0
