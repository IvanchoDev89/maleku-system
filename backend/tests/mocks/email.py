"""Mock email service (Resend) for testing."""

from unittest.mock import MagicMock


class MockResendResponse:
    id: str = "mock_email_123"
    from_email: str = "test@costaricatravel.dev"
    to: list = ["recipient@example.com"]
    subject: str = "Test"
    html: str = "<p>Test</p>"


def mock_resend_module():
    """Patch `import resend` to return this mock.

    Usage in conftest:
        monkeypatch.setitem(sys.modules, "resend", mock_resend_module())
    """
    mock = MagicMock()
    mock.Emails = MagicMock()
    mock.Emails.send = MagicMock(return_value=MockResendResponse())
    return mock


class EmailCapture:
    """Capture sent emails for assertion in tests."""

    def __init__(self):
        self.sent: list[dict] = []

    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        from_email: str = "test@costaricatravel.dev",
    ) -> dict:
        payload = {"to": to, "subject": subject, "from": from_email}
        self.sent.append(payload)
        return {"id": f"mock_{len(self.sent)}", **payload}

    def last_email(self) -> dict | None:
        return self.sent[-1] if self.sent else None

    def reset(self):
        self.sent.clear()
