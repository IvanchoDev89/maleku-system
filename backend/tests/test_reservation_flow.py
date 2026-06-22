"""
Integration test: Flujo completo de reservas.
Covers property detail → availability → pricing → booking → calendar management.

Run with:
    cd backend && python -m pytest tests/test_reservation_flow.py -v -x

All test data is created and cleaned up via the API, no direct DB access needed.
"""

import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

NOW = datetime.now(timezone.utc)
CI = (NOW + timedelta(days=45)).strftime("%Y-%m-%dT00:00:00Z")  # check-in (45d out)
CO = (NOW + timedelta(days=48)).strftime("%Y-%m-%dT00:00:00Z")  # check-out (48d out)


class TestReservationFlow:
    """Complete reservation flow from property listing to booking verification."""

    async def test_01_health_check(self, client: AsyncClient):
        """Backend is alive."""
        resp = await client.get("/health")
        assert resp.status_code in (200, 404)  # 404 is fine if no health route
        assert resp.status_code < 500

    async def test_02_list_properties(self, client: AsyncClient):
        """Properties list endpoint works."""
        resp = await client.get("/api/v1/properties", params={"limit": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    async def test_03_property_detail_has_rooms_and_vendor(self, client: AsyncClient):
        """Property detail includes rooms and vendor."""
        resp = await client.get("/api/v1/properties/slug/hotel-tamarindo")
        assert resp.status_code == 200
        data = resp.json()
        assert "rooms" in data, "Response must include rooms"
        assert "vendor" in data, "Response must include vendor"
        assert len(data["rooms"]) > 0, "Property should have rooms"
        room = data["rooms"][0]
        assert "price_per_night" in room
        self.__class__.test_room_id = room["id"]
        self.__class__.test_property_id = data["id"]

    async def test_04_availability_check_available(self, client: AsyncClient):
        """Available dates return available=true."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id from previous test")
        resp = await client.post(
            "/api/v1/availability/rooms/check",
            json={
                "room_id": self.__class__.test_room_id,
                "check_in": CI,
                "check_out": CO,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is True

    async def test_05_calendar_returns_dates(self, client: AsyncClient):
        """Calendar returns daily entries."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        resp = await client.get(
            f"/api/v1/availability/rooms/{self.__class__.test_room_id}/calendar",
            params={"start_date": CI, "days": 31},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "dates" in data
        assert len(data["dates"]) == 31

    async def test_06_next_available(self, client: AsyncClient):
        """Next available returns ranges."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        resp = await client.get(
            f"/api/v1/availability/rooms/{self.__class__.test_room_id}/next-available",
            params={"nights": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "available_ranges" in data
        assert len(data["available_ranges"]) > 0

    async def test_07_vendor_blocks_dates(self, vendor_auth_client: AsyncClient):
        """Vendor blocks dates via calendar PUT."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        block_date = datetime.fromisoformat(CI.replace("Z", "+00:00"))
        resp = await vendor_auth_client.put(
            f"/api/v1/availability/rooms/{self.__class__.test_room_id}/calendar",
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
        assert resp.status_code == 200
        data = resp.json()
        assert data["updated_count"] == 2
        assert "Calendar updated" in data["message"]

    async def test_08_calendar_reflects_blocked_dates(self, client: AsyncClient):
        """Calendar shows blocked state from vendor update."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        block_date = datetime.fromisoformat(CI.replace("Z", "+00:00"))
        resp = await client.get(
            f"/api/v1/availability/rooms/{self.__class__.test_room_id}/calendar",
            params={"start_date": block_date.strftime("%Y-%m-%dT00:00:00Z"), "days": 3},
        )
        assert resp.status_code == 200
        data = resp.json()
        dates_map = {d["date"]: d for d in data["dates"]}
        d0 = block_date.strftime("%Y-%m-%d")
        d1 = (block_date + timedelta(days=1)).strftime("%Y-%m-%d")
        assert d0 in dates_map
        assert d1 in dates_map
        assert dates_map[d0]["available"] is False
        assert dates_map[d1]["available"] is True
        assert dates_map[d1].get("price_override") == 200.0

    async def test_09_price_preview(self, auth_client: AsyncClient):
        """Price preview returns correct breakdown."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        ci = datetime.fromisoformat(CI.replace("Z", "+00:00"))
        co = ci + timedelta(days=4)
        resp = await auth_client.post(
            "/api/v1/bookings/preview",
            json={
                "room_id": self.__class__.test_room_id,
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
                "guests": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["nights"] == 4
        assert data["subtotal"] > 0
        assert data["total"] > 0

    async def test_10_create_property_booking(self, auth_client: AsyncClient):
        """Create a property booking."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id/ property_id")
        ci = datetime.fromisoformat(CI.replace("Z", "+00:00"))
        co = ci + timedelta(days=3)
        resp = await auth_client.post(
            "/api/v1/bookings/property",
            json={
                "property_id": self.__class__.test_property_id,
                "room_id": self.__class__.test_room_id,
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
                "guests": 2,
                "guest_name": "Integration Test",
                "guest_email": "e2e@test.com",
                "guest_phone": "+50670000000",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["booking_type"] == "property"
        assert data["status"] == "pending"
        assert data["total_amount"] > 0
        self.__class__.test_booking_id = data["id"]

    async def test_11_booking_blocks_availability(self, client: AsyncClient):
        """After booking, dates become unavailable."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        ci = datetime.fromisoformat(CI.replace("Z", "+00:00"))
        co = ci + timedelta(days=3)
        resp = await client.post(
            "/api/v1/availability/rooms/check",
            json={
                "room_id": self.__class__.test_room_id,
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["available"] is False, "Booking should block availability"
        assert len(data["alternative_dates"]) > 0, "Should suggest alternatives"

    async def test_12_cannot_double_book(self, auth_client: AsyncClient):
        """Double-booking same dates is rejected."""
        if not hasattr(self.__class__, "test_room_id"):
            pytest.skip("No room_id")
        ci = datetime.fromisoformat(CI.replace("Z", "+00:00"))
        co = ci + timedelta(days=3)
        resp = await auth_client.post(
            "/api/v1/bookings/property",
            json={
                "property_id": self.__class__.test_property_id,
                "room_id": self.__class__.test_room_id,
                "check_in": ci.strftime("%Y-%m-%dT00:00:00Z"),
                "check_out": co.strftime("%Y-%m-%dT00:00:00Z"),
                "guests": 2,
                "guest_name": "Double Book",
                "guest_email": "double@test.com",
                "guest_phone": "+50670000001",
            },
        )
        assert resp.status_code in (409, 400), (
            f"Expected 409/400 conflict, got {resp.status_code}"
        )

    async def test_13_get_booking(self, auth_client: AsyncClient):
        """Can retrieve booking by ID."""
        if not hasattr(self.__class__, "test_booking_id"):
            pytest.skip("No booking_id")
        resp = await auth_client.get(
            f"/api/v1/bookings/{self.__class__.test_booking_id}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == self.__class__.test_booking_id
        assert data["status"] == "pending"

    async def test_14_tour_booking(self, auth_client: AsyncClient, client: AsyncClient):
        """Create a tour booking via API."""
        # Get first available tour
        resp = await client.get("/api/v1/tours", params={"limit": 1})
        assert resp.status_code == 200
        tours = resp.json().get("items", [])
        if not tours:
            pytest.skip("No tours available in database")
        tour = tours[0]
        booking_date = (NOW + timedelta(days=50)).strftime("%Y-%m-%dT00:00:00Z")

        resp = await auth_client.post(
            "/api/v1/bookings/tour",
            json={
                "tour_id": tour["id"],
                "booking_date": booking_date,
                "participants": 2,
                "guest_name": "Tour E2E",
                "guest_email": "toure2e@test.com",
                "guest_phone": "+50670000002",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["booking_type"] == "tour"
        assert data["status"] == "pending"
        assert data["total_amount"] > 0
