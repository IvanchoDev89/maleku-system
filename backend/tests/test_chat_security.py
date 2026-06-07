"""
Security tests for the chat module (OWASP API1:2023 - BOLA).

Verifies that a user can only read/write conversations they participate in.
"""
import pytest

pytestmark = pytest.mark.security


async def _register_vendor(client, sample_user_data, sample_vendor_data, suffix=""):
    """Helper: register a vendor user and create their vendor profile."""
    payload = sample_user_data.copy()
    payload["email"] = f"vendor{suffix}@example.com"
    reg = await client.post("/api/v1/auth/register/vendor", json=payload, params=sample_vendor_data)
    assert reg.status_code == 200, reg.text
    return reg.json()


@pytest.mark.asyncio
async def test_user_can_read_own_conversation(
    client, sample_user_data, sample_vendor_data
):
    """User who created a conversation can read it."""
    reg = await _register_vendor(client, sample_user_data, sample_vendor_data)
    user_token = reg["access_token"]
    vendor_id = reg["user"]["id"]  # actually user id, we will fetch vendor later

    # Create a conversation as the user
    # First we need the vendor.id (not user.id). The /register/vendor response
    # usually includes the user; for the conversation we need the vendor UUID.
    # We'll use the public /vendors endpoint to find one matching the business.
    vendors_resp = await client.get("/api/v1/vendors")
    if vendors_resp.status_code != 200 or not vendors_resp.json():
        pytest.skip("No vendors available to create a conversation against")
    vendor_id = vendors_resp.json()[0]["id"]

    conv_resp = await client.post(
        "/api/v1/chat/",
        json={"participant_vendor_id": vendor_id},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert conv_resp.status_code == 200, conv_resp.text
    conv_id = conv_resp.json()["id"]

    # Now the same user reads the conversation
    get_resp = await client.get(
        f"/api/v1/chat/{conv_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == conv_id


@pytest.mark.asyncio
async def test_other_user_cannot_read_conversation(
    client, sample_user_data, sample_vendor_data
):
    """SECURITY (BOLA): a different authenticated user must NOT be able to read
    a conversation they don't participate in."""
    # Set up vendor + first user + conversation
    reg_v = await _register_vendor(client, sample_user_data, sample_vendor_data, "-v")
    user1_token = reg_v["access_token"]

    vendors_resp = await client.get("/api/v1/vendors")
    if vendors_resp.status_code != 200 or not vendors_resp.json():
        pytest.skip("No vendors available to create a conversation against")
    vendor_id = vendors_resp.json()[0]["id"]

    conv_resp = await client.post(
        "/api/v1/chat/",
        json={"participant_vendor_id": vendor_id},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert conv_resp.status_code == 200, conv_resp.text
    conv_id = conv_resp.json()["id"]

    # Register a second, unrelated user
    second_user_data = sample_user_data.copy()
    second_user_data["email"] = "intruder@example.com"
    second_reg = await client.post("/api/v1/auth/register", json=second_user_data)
    assert second_reg.status_code == 200, second_reg.text
    intruder_token = second_reg.json()["access_token"]

    # The intruder attempts to read the conversation
    resp = await client.get(
        f"/api/v1/chat/{conv_id}",
        headers={"Authorization": f"Bearer {intruder_token}"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_other_user_cannot_get_messages(
    client, sample_user_data, sample_vendor_data
):
    """SECURITY (BOLA): a different user must NOT be able to read messages."""
    reg_v = await _register_vendor(client, sample_user_data, sample_vendor_data, "-m")
    user1_token = reg_v["access_token"]

    vendors_resp = await client.get("/api/v1/vendors")
    if vendors_resp.status_code != 200 or not vendors_resp.json():
        pytest.skip("No vendors available")
    vendor_id = vendors_resp.json()[0]["id"]

    conv_resp = await client.post(
        "/api/v1/chat/",
        json={"participant_vendor_id": vendor_id},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert conv_resp.status_code == 200, conv_resp.text
    conv_id = conv_resp.json()["id"]

    second_user_data = sample_user_data.copy()
    second_user_data["email"] = "spy@example.com"
    second_reg = await client.post("/api/v1/auth/register", json=second_user_data)
    intruder_token = second_reg.json()["access_token"]

    resp = await client.get(
        f"/api/v1/chat/{conv_id}/messages",
        headers={"Authorization": f"Bearer {intruder_token}"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"


@pytest.mark.asyncio
async def test_other_user_cannot_send_message(
    client, sample_user_data, sample_vendor_data
):
    """SECURITY (BOLA): a non-participant must NOT be able to post messages."""
    reg_v = await _register_vendor(client, sample_user_data, sample_vendor_data, "-s")
    user1_token = reg_v["access_token"]

    vendors_resp = await client.get("/api/v1/vendors")
    if vendors_resp.status_code != 200 or not vendors_resp.json():
        pytest.skip("No vendors available")
    vendor_id = vendors_resp.json()[0]["id"]

    conv_resp = await client.post(
        "/api/v1/chat/",
        json={"participant_vendor_id": vendor_id},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert conv_resp.status_code == 200, conv_resp.text
    conv_id = conv_resp.json()["id"]

    second_user_data = sample_user_data.copy()
    second_user_data["email"] = "attacker@example.com"
    second_reg = await client.post("/api/v1/auth/register", json=second_user_data)
    attacker_token = second_reg.json()["access_token"]

    resp = await client.post(
        f"/api/v1/chat/{conv_id}/messages",
        json={"content": "I shouldn't be able to post here"},
        headers={"Authorization": f"Bearer {attacker_token}"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_other_user_cannot_mark_read(
    client, sample_user_data, sample_vendor_data
):
    """SECURITY (BOLA): a non-participant must NOT be able to mark messages as read."""
    reg_v = await _register_vendor(client, sample_user_data, sample_vendor_data, "-r")
    user1_token = reg_v["access_token"]

    vendors_resp = await client.get("/api/v1/vendors")
    if vendors_resp.status_code != 200 or not vendors_resp.json():
        pytest.skip("No vendors available")
    vendor_id = vendors_resp.json()[0]["id"]

    conv_resp = await client.post(
        "/api/v1/chat/",
        json={"participant_vendor_id": vendor_id},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert conv_resp.status_code == 200, conv_resp.text
    conv_id = conv_resp.json()["id"]

    second_user_data = sample_user_data.copy()
    second_user_data["email"] = "sneaky@example.com"
    second_reg = await client.post("/api/v1/auth/register", json=second_user_data)
    sneaky_token = second_reg.json()["access_token"]

    resp = await client.post(
        f"/api/v1/chat/{conv_id}/read",
        headers={"Authorization": f"Bearer {sneaky_token}"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
