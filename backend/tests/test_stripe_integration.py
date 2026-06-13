import pytest

pytestmark = pytest.mark.asyncio


class TestStripeEndpoints:
    async def test_create_payment_intent_requires_auth(self, client):
        response = await client.post(
            "/api/v1/stripe/create-payment-intent",
            json={
                "booking_id": "00000000-0000-0000-0000-000000000000",
                "amount": 10000,
            },
        )
        assert response.status_code == 401

    async def test_stripe_webhook_rejected_without_signature(self, client):
        response = await client.post(
            "/api/v1/stripe/webhook",
            json={
                "type": "payment_intent.succeeded",
                "data": {"object": {"id": "pi_test"}},
            },
        )
        assert response.status_code in (400, 422)

    async def test_get_stripe_config(self, client):
        response = await client.get("/api/v1/stripe/config")
        assert response.status_code == 200
        data = response.json()
        assert "publishable_key" in data


class TestStripeConnect:
    async def test_create_account_link_requires_auth(self, client):
        response = await client.post("/api/v1/stripe/connect/account-link")
        assert response.status_code == 401

    async def test_connect_onboarding_requires_auth(self, client):
        response = await client.post("/api/v1/stripe/connect/onboarding")
        assert response.status_code == 401
