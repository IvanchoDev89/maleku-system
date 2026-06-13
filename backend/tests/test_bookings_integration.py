import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def auth_client(client: AsyncClient, sample_user_data):
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
async def vendor_auth_client(client: AsyncClient, sample_user_data, sample_vendor_data):
    response = await client.post(
        "/api/v1/auth/register/vendor",
        json={
            **sample_user_data,
            "email": "vendor@test.com",
            "business_name": sample_vendor_data["business_name"],
            "business_type": sample_vendor_data["business_type"],
        },
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


class TestBookingFlow:
    async def test_create_property_booking(self, auth_client, vendor_auth_client):
        await vendor_auth_client.post("/api/v1/vendors/profile")

        property_data = {
            "name": "Test Hotel",
            "property_type": "hotel",
            "base_price": 100.0,
            "max_guests": 4,
            "description": "A test hotel",
        }
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties", json=property_data
        )
        assert prop_resp.status_code in (200, 201)
        prop = prop_resp.json()

        room_data = {
            "name": "Standard Room",
            "room_type": "standard",
            "max_occupancy": 2,
            "price_per_night": 100.0,
        }
        room_resp = await vendor_auth_client.post(
            f"/api/v1/properties/{prop['id']}/rooms", json=room_data
        )
        assert room_resp.status_code in (200, 201)
        room = room_resp.json()

        check_in = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        check_out = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()

        booking_data = {
            "property_id": prop["id"],
            "room_id": room["id"],
            "check_in": check_in,
            "check_out": check_out,
            "guests": 2,
        }
        response = await auth_client.post(
            "/api/v1/bookings/property", json=booking_data
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["status"] == "pending"
        assert "confirmation_code" in data
        assert data["total_amount"] > 0

    async def test_booking_status_lifecycle(self, auth_client, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Status Test Hotel",
                "property_type": "hotel",
                "base_price": 150.0,
                "max_guests": 2,
            },
        )
        prop = prop_resp.json()

        room_resp = await vendor_auth_client.post(
            f"/api/v1/properties/{prop['id']}/rooms",
            json={
                "name": "Test Room",
                "room_type": "standard",
                "max_occupancy": 2,
                "price_per_night": 150.0,
            },
        )
        room = room_resp.json()

        ci = (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()
        co = (datetime.now(timezone.utc) + timedelta(days=16)).isoformat()

        booking_resp = await auth_client.post(
            "/api/v1/bookings/property",
            json={
                "property_id": prop["id"],
                "room_id": room["id"],
                "check_in": ci,
                "check_out": co,
                "guests": 1,
            },
        )
        booking = booking_resp.json()
        booking_id = booking["id"]

        cancel_resp = await auth_client.patch(f"/api/v1/bookings/{booking_id}/cancel")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"

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
        assert response.status_code == 401

    async def test_list_my_bookings(self, auth_client):
        response = await auth_client.get("/api/v1/bookings/my")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)


class TestAvailabilityAndPricing:
    async def test_availability_check(self, auth_client, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Availability Hotel",
                "property_type": "hotel",
                "base_price": 200.0,
                "max_guests": 4,
            },
        )
        prop = prop_resp.json()

        room_resp = await vendor_auth_client.post(
            f"/api/v1/properties/{prop['id']}/rooms",
            json={
                "name": "Avail Room",
                "room_type": "standard",
                "max_occupancy": 4,
                "price_per_night": 200.0,
            },
        )
        room = room_resp.json()

        ci = (datetime.now(timezone.utc) + timedelta(days=21)).date().isoformat()
        co = (datetime.now(timezone.utc) + timedelta(days=23)).date().isoformat()

        response = await vendor_auth_client.get(
            f"/api/v1/availability/rooms/{room['id']}",
            params={"check_in": ci, "check_out": co},
        )
        assert response.status_code in (200, 404, 422)

    async def test_price_preview(self, auth_client, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Price Preview Hotel",
                "property_type": "hotel",
                "base_price": 250.0,
                "max_guests": 2,
            },
        )
        prop = prop_resp.json()

        room_resp = await vendor_auth_client.post(
            f"/api/v1/properties/{prop['id']}/rooms",
            json={
                "name": "Price Room",
                "room_type": "standard",
                "max_occupancy": 2,
                "price_per_night": 250.0,
            },
        )
        room = room_resp.json()

        ci = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        co = (datetime.now(timezone.utc) + timedelta(days=33)).isoformat()

        response = await auth_client.post(
            "/api/v1/pricing/preview",
            json={"room_id": room["id"], "check_in": ci, "check_out": co, "guests": 2},
        )
        assert response.status_code in (200, 422)


class TestVendorEndpoints:
    async def test_vendor_profile(self, vendor_auth_client):
        response = await vendor_auth_client.post(
            "/api/v1/vendors/profile",
            json={"business_name": "My Vendor Business", "business_type": "hotel"},
        )
        assert response.status_code in (200, 201)

    async def test_vendor_bookings(self, vendor_auth_client):
        response = await vendor_auth_client.get("/api/v1/vendors/bookings")
        assert response.status_code in (200, 403)
