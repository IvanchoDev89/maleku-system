"""
Unit tests for Stripe schemas
"""
import pytest
from uuid import uuid4


class TestStripeSchemas:
    def test_checkout_request_valid(self):
        from app.api.v1.stripe import CheckoutRequest
        booking_id = uuid4()
        data = CheckoutRequest(
            booking_id=booking_id,
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel"
        )
        assert data.booking_id == booking_id
        assert "localhost" in data.success_url

    def test_checkout_request_invalid_url(self):
        from app.api.v1.stripe import CheckoutRequest
        with pytest.raises(ValueError, match="Invalid redirect URL"):
            CheckoutRequest(
                booking_id=uuid4(),
                success_url="https://evil.com/phish",
                cancel_url="https://costaricatravel.dev/cancel"
            )

    def test_checkout_request_no_url(self):
        from app.api.v1.stripe import CheckoutRequest
        with pytest.raises(ValueError, match="Invalid redirect URL"):
            CheckoutRequest(
                booking_id=uuid4(),
                success_url="not-a-url",
                cancel_url="also-not-a-url"
            )

    def test_checkout_response(self):
        from app.api.v1.stripe import CheckoutResponse
        data = CheckoutResponse(
            session_id="cs_test_abc123",
            checkout_url="https://checkout.stripe.com/cs_test_abc123"
        )
        assert data.session_id == "cs_test_abc123"
        assert "stripe.com" in data.checkout_url

    def test_refund_request_empty(self):
        from app.api.v1.stripe import RefundRequest
        data = RefundRequest()
        assert data.amount is None
        assert data.reason is None

    def test_refund_request_with_amount(self):
        from app.api.v1.stripe import RefundRequest
        data = RefundRequest(amount=50.0, reason="customer_request")
        assert data.amount == 50.0
        assert data.reason == "customer_request"

    def test_vendor_connect_response(self):
        from app.api.v1.stripe import VendorConnectResponse
        data = VendorConnectResponse(
            account_id="acct_abc123",
            onboarding_url="https://connect.stripe.com/onboard",
            status="pending"
        )
        assert data.account_id == "acct_abc123"
        assert data.status == "pending"
