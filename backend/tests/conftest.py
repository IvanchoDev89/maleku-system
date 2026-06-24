"""
Test configuration with async database support.
"""

import os

os.environ["ENVIRONMENT"] = "test"

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient

from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.main import app
from app.models import User, UserRole


# Use real PostgreSQL for tests (models use PostgreSQL-specific types).
# Override with TEST_DATABASE_URL env var in CI.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres@127.0.0.1:5432/costaricatravel_test",
)


@pytest_asyncio.fixture(scope="session")
async def schema_engine():
    """Create schema ONCE per session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def engine(schema_engine):
    """Function-scoped engine — each test has its own pool, no schema cost."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_size=1,
        max_overflow=0,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Provide a fresh session per test with automatic table cleanup."""
    session = AsyncSession(engine, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        async with engine.begin() as conn:
            tables = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
            if tables:
                await conn.execute(sa.text(f"TRUNCATE TABLE {tables} CASCADE"))


@pytest_asyncio.fixture
async def client(db_session):
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "phone": "+50612345678",
    }


@pytest.fixture
def sample_vendor_data():
    """Sample vendor data for tests"""
    return {"business_name": "Test Hotel Costa Rica", "business_type": "hotel"}


@pytest.fixture
def sample_property_data():
    """Sample property data for tests"""
    return {
        "name": "Hotel Paradise",
        "slug": "hotel-paradise-abc123",
        "description": "Beautiful beachfront hotel",
        "property_type": "hotel",
        "base_price": 150.0,
        "currency": "USD",
        "max_guests": 4,
    }


@pytest.fixture
def sample_room_data():
    """Sample room data for tests"""
    return {
        "name": "Ocean View Suite",
        "slug": "ocean-view-suite-abc123",
        "room_type": "suite",
        "max_occupancy": 2,
        "price_per_night": 150.0,
        "weekend_price": 180.0,
        "currency": "USD",
    }


# ---------------------------------------------------------------------------
# Security fixtures: admin / superadmin / vendor-without-profile
# ---------------------------------------------------------------------------


async def _create_user_with_role(
    db_session: AsyncSession,
    email: str,
    role: UserRole,
    full_name: str = "Test User",
) -> User:
    """Insert a user directly (bypassing the public /auth/register)."""
    user = User(
        email=email,
        password_hash=get_password_hash("TestPass123!"),
        full_name=full_name,
        role=role,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session) -> User:
    return await _create_user_with_role(
        db_session, "admin@example.com", UserRole.ADMIN, "Admin User"
    )


@pytest_asyncio.fixture
async def superadmin_user(db_session) -> User:
    return await _create_user_with_role(
        db_session, "superadmin@example.com", UserRole.SUPER_ADMIN, "Super Admin"
    )


@pytest_asyncio.fixture
async def vendor_no_profile_user(db_session) -> User:
    """A VENDOR-role user without a Vendor profile (edge case for BOLA-vendor-None)."""
    return await _create_user_with_role(
        db_session,
        "vendor-no-profile@example.com",
        UserRole.VENDOR,
        "Vendor No Profile",
    )


@pytest_asyncio.fixture
async def second_user(db_session) -> User:
    return await _create_user_with_role(
        db_session, "user2@example.com", UserRole.CLIENT, "Second User"
    )


def _auth_header(user: User) -> dict[str, str]:
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_client(client, admin_user):
    client.headers.update(_auth_header(admin_user))
    return client


@pytest_asyncio.fixture
async def superadmin_client(client, superadmin_user):
    client.headers.update(_auth_header(superadmin_user))
    return client


@pytest_asyncio.fixture
async def vendor_no_profile_client(client, vendor_no_profile_user):
    client.headers.update(_auth_header(vendor_no_profile_user))
    return client


@pytest_asyncio.fixture
async def second_client(client, second_user):
    client.headers.update(_auth_header(second_user))
    return client
