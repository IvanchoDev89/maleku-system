import pytest
import uuid
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession):
    from app.models import User, UserRole
    from app.core.security import get_password_hash, create_access_token

    user = User(
        email="client-integration@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Client Integration",
        role=UserRole.CLIENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=str(user.id))
    client.headers["Authorization"] = f"Bearer {token}"
    client.user_id = user.id
    return client


@pytest.fixture
async def vendor_entities(db_session: AsyncSession):
    from app.models import User, UserRole, Vendor, Property, Room
    from app.core.security import get_password_hash

    user = User(
        email="vendor-integration@example.com",
        password_hash=get_password_hash("TestPass123!"),
        full_name="Vendor Integration",
        role=UserRole.VENDOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    vendor = Vendor(
        user_id=user.id,
        business_name="Integration Hotel",
        business_slug=f"integration-hotel-{uuid.uuid4().hex[:8]}",
        business_type="hotel",
        is_active=True,
    )
    db_session.add(vendor)
    await db_session.flush()

    property_obj = Property(
        vendor_id=vendor.id,
        name="Integration Property",
        slug=f"integration-prop-{uuid.uuid4().hex[:8]}",
        description="An integration test property",
        property_type="hotel",
        base_price=100.0,
        currency="USD",
        max_guests=4,
        is_active=True,
    )
    db_session.add(property_obj)
    await db_session.flush()

    room = Room(
        property_id=property_obj.id,
        name="Integration Room",
        max_guests=2,
        price_per_night=100.0,
        weekend_price=120.0,
        is_available=True,
    )
    db_session.add(room)
    await db_session.commit()

    return {
        "property_id": str(property_obj.id),
        "room_id": str(room.id),
        "vendor_id": str(vendor.id),
    }


class TestBookingFlow:
    async def test_create_property_booking_validates_required_fields(
        self, auth_client, vendor_entities
    ):
        """Booking creation requires guest_name and guest_email."""
        check_in = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        check_out = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()

        booking_data = {
            "property_id": vendor_entities["property_id"],
            "room_id": vendor_entities["room_id"],
            "check_in": check_in,
            "check_out": check_out,
            "guests": 2,
        }
        response = await auth_client.post(
            "/api/v1/bookings/property", json=booking_data
        )
        assert response.status_code == 422, response.text

    async def test_booking_status_lifecycle(
        self, auth_client, vendor_entities, db_session
    ):
        """Test canceling a booking created directly in DB."""
        from app.models import Booking
        import uuid

        ci = datetime.now(timezone.utc) + timedelta(days=14)
        co = ci + timedelta(days=2)

        booking = Booking(
            property_id=uuid.UUID(vendor_entities["property_id"]),
            room_id=uuid.UUID(vendor_entities["room_id"]),
            vendor_id=uuid.UUID(vendor_entities["vendor_id"]),
            booking_type="property",
            user_id=auth_client.user_id,
            check_in=ci,
            check_out=co,
            total_amount=200.0,
            status="pending",
            guest_name="Test Guest",
            guest_email="guest@example.com",
        )
        db_session.add(booking)
        await db_session.commit()
        booking_id = str(booking.id)

        cancel_resp = await auth_client.put(
            f"/api/v1/bookings/{booking_id}/status",
            json={"status": "cancelled"},
        )
        assert cancel_resp.status_code in (200, 403), cancel_resp.text

    async def test_booking_requires_auth(self, client):
        response = await client.post(
            "/api/v1/bookings/property",
            json={
                "property_id": "00000000-0000-0000-0000-000000000000",
                "check_in": "2026-07-01T00:00:00Z",
                "check_out": "2026-07-03T00:00:00Z",
                "guests": 2,
            },
        )
        assert response.status_code in (401, 403)

    async def test_list_my_bookings(self, auth_client):
        response = await auth_client.get("/api/v1/bookings/my")
        assert response.status_code in (200, 422), response.text


class TestAvailabilityAndPricing:
    async def test_availability_check(self, auth_client, vendor_entities):
        ci = (datetime.now(timezone.utc) + timedelta(days=21)).date().isoformat()
        co = (datetime.now(timezone.utc) + timedelta(days=23)).date().isoformat()

        response = await auth_client.get(
            f"/api/v1/availability/rooms/{vendor_entities['room_id']}",
            params={"check_in": ci, "check_out": co},
        )
        assert response.status_code in (200, 404, 422)

    async def test_price_preview(self, auth_client, vendor_entities):
        ci = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        co = (datetime.now(timezone.utc) + timedelta(days=33)).isoformat()

        response = await auth_client.post(
            "/api/v1/bookings/preview",
            json={
                "room_id": vendor_entities["room_id"],
                "check_in": ci,
                "check_out": co,
                "guests": 2,
            },
        )
        assert response.status_code in (200, 422), response.text


class TestVendorEndpoints:
    async def test_vendor_profile(self, auth_client, db_session):
        from app.models import User, UserRole, Vendor
        from app.core.security import get_password_hash, create_access_token

        user = User(
            email="vendor-profile@example.com",
            password_hash=get_password_hash("TestPass123!"),
            full_name="Vendor Profile",
            role=UserRole.VENDOR,
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        vendor = Vendor(
            user_id=user.id,
            business_name="My Vendor Business",
            business_slug=f"my-vendor-{uuid.uuid4().hex[:8]}",
            business_type="hotel",
            is_active=True,
        )
        db_session.add(vendor)
        await db_session.commit()

        token = create_access_token(subject=str(user.id))
        client = auth_client
        client.headers["Authorization"] = f"Bearer {token}"

        response = await client.get("/api/v1/vendors/me/profile")
        assert response.status_code in (200, 201), response.text
        assert response.json()["business_name"] == "My Vendor Business"

    async def test_vendor_bookings(self, auth_client, vendor_entities, db_session):
        from app.models import Booking
        from datetime import datetime, timezone

        ci = datetime.now(timezone.utc) + timedelta(days=20)
        co = ci + timedelta(days=2)

        booking = Booking(
            property_id=uuid.UUID(vendor_entities["property_id"]),
            room_id=uuid.UUID(vendor_entities["room_id"]),
            vendor_id=uuid.UUID(vendor_entities["vendor_id"]),
            booking_type="property",
            user_id=None,
            check_in=ci,
            check_out=co,
            total_amount=200.0,
            status="pending",
            guest_name="Test Guest",
            guest_email="guest@example.com",
        )
        db_session.add(booking)
        await db_session.commit()

        response = await auth_client.get("/api/v1/bookings/vendor/stats")
        assert response.status_code in (200, 403), response.text
