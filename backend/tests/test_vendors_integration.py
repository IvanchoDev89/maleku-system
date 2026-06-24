import pytest

pytestmark = pytest.mark.asyncio


class TestVendorRegistration:
    async def test_register_vendor(self, client, sample_user_data):
        response = await client.post(
            "/api/v1/auth/register/vendor",
            json={
                **sample_user_data,
                "email": "vendor-reg@test.com",
                "business_name": "Test Vendor Co",
                "business_type": "hotel",
            },
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert data["user"]["role"] == "vendor"

    async def test_register_vendor_missing_business_name(
        self, client, sample_user_data
    ):
        response = await client.post(
            "/api/v1/auth/register/vendor",
            json={**sample_user_data, "email": "vendor-no-business@test.com"},
        )
        assert response.status_code == 422

    async def test_register_vendor_duplicate_email(self, client, sample_user_data):
        await client.post(
            "/api/v1/auth/register/vendor",
            json={
                **sample_user_data,
                "email": "vendor-dup@test.com",
                "business_name": "First Vendor",
                "business_type": "hotel",
            },
        )
        response = await client.post(
            "/api/v1/auth/register/vendor",
            json={
                **sample_user_data,
                "email": "vendor-dup@test.com",
                "business_name": "Second Vendor",
                "business_type": "tour",
            },
        )
        assert response.status_code == 400


class TestVendorListings:
    async def test_list_vendors_public(self, client):
        response = await client.get("/api/v1/vendors")
        assert response.status_code == 200

    async def test_vendor_analytics_requires_auth(self, client):
        response = await client.get("/api/v1/vendors/me/analytics")
        assert response.status_code in (401, 403)
