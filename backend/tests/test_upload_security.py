"""
Security tests for the upload module.

Verifies:
- File extension whitelist
- Content-Type whitelist
- Magic-bytes validation (defense against polyglot files)
- BOLA fix: non-admin users cannot delete uploads
- SVG is no longer accepted (stored-XSS mitigation)
"""

import io
import pytest
from PIL import Image

pytestmark = pytest.mark.security


def _png_bytes() -> bytes:
    """Generate a tiny in-memory PNG image (1x1 red pixel)."""
    img = Image.new("RGB", (1, 1), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _jpeg_bytes() -> bytes:
    img = Image.new("RGB", (1, 1), color=(0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_upload_rejects_svg_extension(client, auth_token=None):
    """SVG uploads must be rejected (stored XSS prevention)."""
    svg_content = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    files = {"file": ("evil.svg", io.BytesIO(svg_content), "image/svg+xml")}
    resp = await client.post(
        "/api/v1/upload/image", files=files, data={"folder": "general"}
    )
    assert resp.status_code == 400, (
        f"Expected 400 for SVG, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.asyncio
async def test_upload_rejects_polyglot_file(client, sample_user_data):
    """A PHP web shell renamed to .jpg with image/jpeg MIME must be rejected
    by the magic-bytes check."""
    polyglot = b"<?php echo 'pwned'; ?>" + _png_bytes()
    files = {"file": ("shell.jpg", io.BytesIO(polyglot), "image/jpeg")}
    resp = await client.post(
        "/api/v1/upload/image",
        files=files,
        data={"folder": "general"},
        headers={"Authorization": f"Bearer {(await _login(client, sample_user_data))}"},
    )
    # 400 because PIL refuses to parse the bytes as a real PNG
    assert resp.status_code == 400, (
        f"Expected 400 for polyglot, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.asyncio
async def test_upload_accepts_valid_png(client, sample_user_data):
    """Sanity check: a real PNG is accepted when the user is authenticated."""
    token = await _login(client, sample_user_data)
    files = {"file": ("ok.png", io.BytesIO(_png_bytes()), "image/png")}
    resp = await client.post(
        "/api/v1/upload/image",
        files=files,
        data={"folder": "general"},
        headers={"Authorization": f"Bearer {token}"},
    )
    # Cloudinary not configured in tests, so it falls back to local
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_delete_upload_requires_admin(
    client, sample_user_data, vendor_no_profile_client
):
    """SECURITY (BOLA): a non-admin authenticated user must NOT be able to
    delete an upload they do not own."""
    # First, upload a file as the regular user
    token = await _login(client, sample_user_data)
    files = {"file": ("ok.png", io.BytesIO(_png_bytes()), "image/png")}
    upload_resp = await client.post(
        "/api/v1/upload/image",
        files=files,
        data={"folder": "general"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert upload_resp.status_code == 200, upload_resp.text
    url = upload_resp.json()["url"]
    # The path is /uploads/...; the DELETE endpoint wants the filesystem path
    # relative to the upload root, but we can pass the full path and the
    # middleware sanitize_path will validate it. We just need any plausible
    # path under the upload root.
    delete_resp = await vendor_no_profile_client.request(
        "DELETE",
        "/api/v1/upload/image/abc",
        params={"path": url, "provider": "local"},
    )
    # Non-admin (vendor without profile in this test) must be denied
    assert delete_resp.status_code == 403, (
        f"Expected 403 for non-admin delete, got {delete_resp.status_code}: {delete_resp.text}"
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


async def _login(client, sample_user_data) -> str:
    """Register a fresh user and return the access token."""
    payload = sample_user_data.copy()
    # Use a unique email to avoid clashing with other tests
    import uuid as _uuid

    payload["email"] = f"upload-{_uuid.uuid4().hex[:8]}@example.com"
    reg = await client.post("/api/v1/auth/register", json=payload)
    assert reg.status_code == 200, reg.text
    return reg.json()["access_token"]
