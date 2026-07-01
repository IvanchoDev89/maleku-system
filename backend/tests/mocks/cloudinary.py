"""Mock Cloudinary upload service for testing."""

from unittest.mock import MagicMock
from typing import Optional


class MockCloudinaryUploadResult:
    public_id: str = "test/mock_image"
    secure_url: str = "https://res.cloudinary.com/mock/image/upload/v1/test/mock_image"
    format: str = "webp"
    width: int = 800
    height: int = 600
    bytes: int = 10240
    etag: str = "mock_etag_123"


def mock_cloudinary_module():
    """Patch `import cloudinary` to return this mock.

    Usage in conftest:
        import sys
        monkeypatch.setitem(sys.modules, "cloudinary", mock_cloudinary_module())
    """
    mock = MagicMock()
    mock.uploader = MagicMock()
    mock.uploader.upload = MagicMock(return_value=MockCloudinaryUploadResult())
    mock.api = MagicMock()
    mock.api.delete_resources = MagicMock(return_value={"deleted": {"test/mock_image": "deleted"}})
    mock.utils = MagicMock()
    mock.utils.cloudinary_url = MagicMock(return_value=("https://res.cloudinary.com/mock/image/upload/v1/test/mock_image", {}))
    return mock
