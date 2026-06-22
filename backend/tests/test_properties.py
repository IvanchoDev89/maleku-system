import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.core.database import get_db
from app.main import app

pytestmark = pytest.mark.asyncio


async def _make_client(db_session):
    """Create a fresh AsyncClient with the db_session override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://localhost")


@pytest_asyncio.fixture
async def auth_client(db_session, sample_user_data):
    client = await _make_client(db_session)
    try:
        resp = await client.post("/api/v1/auth/register", json=sample_user_data)
        client.headers["Authorization"] = f"Bearer {resp.json()['access_token']}"
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def vendor_auth_client(db_session, sample_user_data, sample_vendor_data):
    client = await _make_client(db_session)
    try:
        resp = await client.post(
            "/api/v1/auth/register/vendor",
            json={
                **sample_user_data,
                "email": "vendor-prop@test.com",
                "business_name": sample_vendor_data["business_name"],
                "business_type": sample_vendor_data["business_type"],
            },
        )
        client.headers["Authorization"] = f"Bearer {resp.json()['access_token']}"
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def second_vendor_client(db_session, sample_user_data, sample_vendor_data):
    client = await _make_client(db_session)
    try:
        resp = await client.post(
            "/api/v1/auth/register/vendor",
            json={
                **sample_user_data,
                "email": "vendor-prop2@test.com",
                "full_name": "Second Vendor",
                "phone": "+50687654321",
                "business_name": "Second Hotel CR",
                "business_type": "hotel",
            },
        )
        client.headers["Authorization"] = f"Bearer {resp.json()['access_token']}"
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture
async def superadmin_vendor_client(db_session, sample_user_data, sample_vendor_data):
    from sqlalchemy import select
    from app.models import User

    client = await _make_client(db_session)
    try:
        resp = await client.post(
            "/api/v1/auth/register/vendor",
            json={
                **sample_user_data,
                "email": "superadmin-vendor@test.com",
                "full_name": "Super Admin Vendor",
                "phone": "+50611111111",
                "business_name": "Super Admin Hotels",
                "business_type": "hotel",
            },
        )
        token = resp.json()["access_token"]
        user_id = resp.json()["user"]["id"]
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.role = "super_admin"
        client.headers["Authorization"] = f"Bearer {token}"
        yield client
    finally:
        await client.aclose()


class TestListProperties:
    async def test_list_properties_public(self, client):
        resp = await client.get("/api/v1/properties")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    async def test_list_properties_with_region_filter(self, client, vendor_auth_client):
        await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Guanacaste Resort",
                "property_type": "hotel",
                "region": "Guanacaste",
                "base_price": 200.0,
                "max_guests": 4,
            },
        )
        resp = await client.get("/api/v1/properties", params={"region": "Guanacaste"})
        assert resp.status_code == 200

    async def test_list_properties_with_type_filter(self, client, vendor_auth_client):
        await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Villa Test",
                "property_type": "villa",
                "base_price": 300.0,
                "max_guests": 8,
            },
        )
        resp = await client.get("/api/v1/properties", params={"property_type": "villa"})
        assert resp.status_code == 200

    async def test_list_properties_with_price_range(self, client, vendor_auth_client):
        await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Budget Inn",
                "property_type": "hotel",
                "base_price": 50.0,
                "max_guests": 2,
            },
        )
        resp = await client.get(
            "/api/v1/properties", params={"min_price": 30.0, "max_price": 100.0}
        )
        assert resp.status_code == 200

    async def test_list_properties_featured(self, client, superadmin_vendor_client):
        await superadmin_vendor_client.post(
            "/api/v1/properties",
            json={
                "name": "Featured Resort",
                "property_type": "resort",
                "base_price": 500.0,
                "max_guests": 10,
                "is_featured": True,
            },
        )
        resp = await client.get("/api/v1/properties", params={"featured": "true"})
        assert resp.status_code == 200


class TestGetProperty:
    async def test_get_property_by_id(self, client, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Get By ID Test",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 2,
            },
        )
        assert prop_resp.status_code in (200, 201)
        prop_id = prop_resp.json()["id"]

        resp = await client.get(f"/api/v1/properties/{prop_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Get By ID Test"

    async def test_get_property_by_slug(self, client, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Slug Test Property",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 2,
            },
        )
        assert prop_resp.status_code in (200, 201)
        slug = prop_resp.json()["slug"]

        resp = await client.get(f"/api/v1/properties/slug/{slug}")
        assert resp.status_code == 200
        assert resp.json()["id"] == prop_resp.json()["id"]

    async def test_get_property_not_found(self, client):
        resp = await client.get(
            "/api/v1/properties/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == 404


class TestCreateProperty:
    async def test_create_property_vendor(self, vendor_auth_client):
        resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "New Hotel",
                "property_type": "hotel",
                "base_price": 120.0,
                "max_guests": 4,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "New Hotel"
        assert data.get("slug") is not None

    async def test_create_property_forbidden_for_client(self, auth_client):
        resp = await auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Client Hotel",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 2,
            },
        )
        assert resp.status_code == 403

    async def test_create_property_requires_auth(self, client):
        resp = await client.post(
            "/api/v1/properties",
            json={
                "name": "Unauth Hotel",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 2,
            },
        )
        assert resp.status_code == 403

    async def test_create_property_mass_assignment_blocked(self, vendor_auth_client):
        resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Secure Hotel",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 4,
                "vendor_id": "00000000-0000-0000-0000-000000000000",
                "rating": 5.0,
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data.get("rating", 0) == 0.0


class TestUpdateProperty:
    async def test_update_property_owner(self, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "My Property",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 4,
            },
        )
        prop_id = prop_resp.json()["id"]

        resp = await vendor_auth_client.put(
            f"/api/v1/properties/{prop_id}",
            json={"name": "Renamed Property", "base_price": 150.0},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed Property"

    async def test_update_property_non_owner_forbidden(
        self, vendor_auth_client, second_vendor_client
    ):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Owned Property",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 4,
            },
        )
        prop_id = prop_resp.json()["id"]

        resp = await second_vendor_client.put(
            f"/api/v1/properties/{prop_id}", json={"name": "Hacked"}
        )
        assert resp.status_code == 403

    async def test_update_property_not_found(self, vendor_auth_client):
        resp = await vendor_auth_client.put(
            "/api/v1/properties/00000000-0000-0000-0000-000000000000",
            json={"name": "Ghost"},
        )
        assert resp.status_code == 404


class TestDeleteProperty:
    async def test_delete_property_owner(self, vendor_auth_client):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Remove Test",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 4,
            },
        )
        prop_id = prop_resp.json()["id"]

        resp = await vendor_auth_client.delete(f"/api/v1/properties/{prop_id}")
        assert resp.status_code == 200

        get_resp = await vendor_auth_client.get(f"/api/v1/properties/{prop_id}")
        assert get_resp.status_code == 200
        assert get_resp.json().get("is_active") is False

    async def test_delete_property_non_owner_forbidden(
        self, vendor_auth_client, second_vendor_client
    ):
        prop_resp = await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Protected Property",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 4,
            },
        )
        prop_id = prop_resp.json()["id"]

        resp = await second_vendor_client.delete(f"/api/v1/properties/{prop_id}")
        assert resp.status_code == 403


class TestVendorProperties:
    async def test_get_my_properties(self, vendor_auth_client):
        await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "My Hotel",
                "property_type": "hotel",
                "base_price": 100.0,
                "max_guests": 4,
            },
        )
        resp = await vendor_auth_client.get("/api/v1/properties/vendor/my")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) >= 1

    async def test_get_my_properties_forbidden_for_client(self, auth_client):
        resp = await auth_client.get("/api/v1/properties/vendor/my")
        assert resp.status_code == 403


class TestRegions:
    async def test_get_regions(self, client, vendor_auth_client):
        await vendor_auth_client.post(
            "/api/v1/properties",
            json={
                "name": "Region Test",
                "property_type": "hotel",
                "region": "Puntarenas",
                "base_price": 100.0,
                "max_guests": 4,
            },
        )
        resp = await client.get("/api/v1/properties/regions")
        assert resp.status_code == 200
        data = resp.json()
        assert "regions" in data
