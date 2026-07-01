"""Mock Stripe API for testing without live credentials."""

from unittest.mock import MagicMock


class MockStripePaymentIntent:
    id: str = "pi_test_mock_123456789"
    amount: int = 5000
    currency: str = "usd"
    status: str = "succeeded"
    client_secret: str = "pi_test_secret_mock"
    metadata: dict = {}
    charges: list = []


class MockStripeCheckoutSession:
    id: str = "cs_test_mock_123456789"
    url: str = "https://checkout.stripe.com/mock"
    payment_status: str = "paid"
    status: str = "complete"
    metadata: dict = {}
    customer: str | None = None
    payment_intent: str = "pi_test_mock_123456789"


class MockStripeAccount:
    id: str = "acct_mock_123456789"
    charges_enabled: bool = True
    payouts_enabled: bool = True
    details_submitted: bool = True


def mock_stripe_module():
    """Patch `import stripe` to return this mock."""
    mock = MagicMock()
    mock.PaymentIntent = MagicMock()
    mock.PaymentIntent.create = MagicMock(return_value=MockStripePaymentIntent())
    mock.PaymentIntent.retrieve = MagicMock(return_value=MockStripePaymentIntent())

    mock.checkout = MagicMock()
    mock.checkout.Session = MagicMock()
    mock.checkout.Session.create = MagicMock(return_value=MockStripeCheckoutSession())
    mock.checkout.Session.retrieve = MagicMock(return_value=MockStripeCheckoutSession())

    mock.Account = MagicMock()
    mock.Account.create = MagicMock(return_value=MockStripeAccount())
    mock.Account.retrieve = MagicMock(return_value=MockStripeAccount())

    mock.Webhook = MagicMock()
    mock.Webhook.construct_event = MagicMock(return_value={"type": "payment_intent.succeeded"})

    mock.error = MagicMock()
    mock.error.StripeError = type("StripeError", (Exception,), {})
    mock.error.CardError = type("CardError", (Exception,), {})
    return mock
