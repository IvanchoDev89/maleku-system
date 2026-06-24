"""
API tests for core endpoints
Tests authentication, properties, tours, destinations, search and bookings
"""

import pytest
from fastapi import status


class TestAuth:
    """Authentication tests"""

    @pytest.mark.asyncio
    async def test_register_user(self, client, sample_user_data):
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == status.HTTP_201_CREATED, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == sample_user_data["email"]
        assert data["user"]["role"] == "client"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, sample_user_data):
        await client.post("/api/v1/auth/register", json=sample_user_data)
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_login(self, client, sample_user_data):
        # First register
        await client.post("/api/v1/auth/register", json=sample_user_data)

        # Then login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": sample_user_data["email"],
                "password": sample_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, sample_user_data):
        await client.post("/api/v1/auth/register", json=sample_user_data)

        response = await client.post(
            "/api/v1/auth/login",
            json={"email": sample_user_data["email"], "password": "WrongPassword1!"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client, sample_user_data):
        weak_data = {**sample_user_data, "password": "123"}
        response = await client.post("/api/v1/auth/register", json=weak_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client, sample_user_data):
        invalid_data = {**sample_user_data, "email": "notanemail"}
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProperties:
    """Properties endpoint tests"""

    @pytest.mark.asyncio
    async def test_get_properties(self, client):
        response = await client.get("/api/v1/properties")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_get_properties_pagination(self, client):
        response = await client.get("/api/v1/properties?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_get_properties_region_filter(self, client):
        response = await client.get("/api/v1/properties?region=Guanacaste")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_properties_invalid_page(self, client):
        response = await client.get("/api/v1/properties?page=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTours:
    """Tours endpoint tests"""

    @pytest.mark.asyncio
    async def test_get_tours(self, client):
        response = await client.get("/api/v1/tours")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_tours_category_filter(self, client):
        response = await client.get("/api/v1/tours?category=adventure")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_tours_difficulty_filter(self, client):
        response = await client.get("/api/v1/tours?difficulty=easy")
        assert response.status_code == status.HTTP_200_OK


class TestDestinations:
    """Destinations endpoint tests"""

    @pytest.mark.asyncio
    async def test_get_destinations(self, client):
        response = await client.get("/api/v1/destinations")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_destinations_region_filter(self, client):
        response = await client.get("/api/v1/destinations?region=Norte")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_get_destinations_featured(self, client):
        response = await client.get("/api/v1/destinations?featured=true")
        assert response.status_code == status.HTTP_200_OK


class TestSearch:
    """Search endpoint tests"""

    @pytest.mark.asyncio
    async def test_search_basic(self, client):
        response = await client.get("/api/v1/search?q=playa")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "properties" in data
        assert "tours" in data
        assert "destinations" in data

    @pytest.mark.asyncio
    async def test_search_empty_query(self, client):
        response = await client.get("/api/v1/search?q=")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_search_long_query(self, client):
        long_query = "a" * 500
        response = await client.get(f"/api/v1/search?q={long_query}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_search_map_endpoint(self, client):
        response = await client.get("/api/v1/search/map")
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_search_map_count(self, client):
        response = await client.get("/api/v1/search/map/count")
        assert response.status_code == status.HTTP_200_OK


class TestHealth:
    """Health check endpoint tests"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_health_endpoint(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_liveness_endpoint(self, client):
        response = await client.get("/health/live")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK


class TestRateLimiting:
    """Rate limiting tests"""

    @pytest.mark.asyncio
    async def test_search_rate_limit(self, client):
        """Verify search endpoint handles requests"""
        for _ in range(5):
            response = await client.get("/api/v1/search?q=test")
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_429_TOO_MANY_REQUESTS,
            ]


class TestBookings:
    """Booking endpoint tests"""

    @pytest.mark.asyncio
    async def test_create_booking_unauthenticated(self, client):
        """Verify unauthenticated requests are rejected"""
        response = await client.post(
            "/api/v1/bookings/property",
            json={
                "property_id": "00000000-0000-0000-0000-000000000000",
                "check_in": "2025-06-01",
                "check_out": "2025-06-05",
                "guests": 2,
            },
        )
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    @pytest.mark.asyncio
    async def test_update_booking_status_unauthenticated(self, client):
        response = await client.put(
            "/api/v1/bookings/00000000-0000-0000-0000-000000000000/status",
            json={"status": "confirmed"},
        )
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
