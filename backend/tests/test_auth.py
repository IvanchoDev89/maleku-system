"""
Tests for authentication endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, sample_user_data):
    """Test user registration"""
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code in (200, 201)

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == sample_user_data["email"]
    assert data["user"]["full_name"] == sample_user_data["full_name"]
    assert data["user"]["role"] == "client"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, sample_user_data):
    """Test registration with duplicate email fails"""
    # Register first user
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Try to register again with same email
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient, sample_user_data):
    """Test registration with invalid email fails"""
    sample_user_data["email"] = "invalid-email"

    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient, sample_user_data):
    """Test registration with weak password fails"""
    sample_user_data["password"] = "weak"

    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code in (400, 422)
    if response.status_code == 400:
        assert "password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, sample_user_data):
    """Test successful login"""
    # Register user first
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Login
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, sample_user_data):
    """Test login with invalid credentials"""
    login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, sample_user_data):
    """Test login with wrong password"""
    # Register user first
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Try to login with wrong password
    login_data = {"email": sample_user_data["email"], "password": "WrongPass123!"}
    response = await client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, sample_user_data):
    """Test getting current user with valid token"""
    # Register and get token
    register_response = await client.post(
        "/api/v1/auth/register", json=sample_user_data
    )
    token = register_response.json()["access_token"]

    # Get current user
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user_data["email"]


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test getting current user without token fails"""
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, sample_user_data):
    """Test token refresh"""
    # Register and get refresh token
    register_response = await client.post(
        "/api/v1/auth/register", json=sample_user_data
    )
    refresh_token = register_response.json()["refresh_token"]

    # Refresh token
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refresh with invalid token fails"""
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid-token"}
    )

    assert response.status_code == 401
