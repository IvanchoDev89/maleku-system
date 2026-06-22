"""
Test configuration with async database support.

Strategy
--------
* Schema is created once per session via ``Base.metadata.create_all`` (the
  tsvector indexes now use raw ``text()`` expressions so they don't break
  ``create_all``).
* Each test runs inside a SAVEPOINT. Anything committed by the endpoint
  under test is automatically rolled back when the test ends, so tests
  cannot leak state to one another.
"""

import os

os.environ["ENVIRONMENT"] = "test"

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient

from app.core.database import Base, get_db
from app.core.security import get_password_hash, create_access_token
from app.main import app
from app.models import User, UserRole

# Prefer a real PostgreSQL connection when DATABASE_URL is provided (matches CI).
# Fall back to in-memory SQLite only when no PostgreSQL is reachable.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://crtravel:crtravel123@127.0.0.1:5432/costaricatravel_test",
)
if not os.environ.get("TEST_DATABASE_URL") and "DATABASE_URL" not in os.environ:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create async engine for tests (one per session)."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Drop and recreate schema to ensure clean types
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Provide a session bound to a SAVEPOINT for clean per-test isolation.

    Pattern: open an outer transaction on a connection, then for each test
    ``begin_nested()`` opens a SAVEPOINT. When the test ends we roll back
    the outer transaction, discarding everything the endpoint committed.
    """
    from sqlalchemy import event

    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)
    await session.begin_nested()

    @event.listens_for(session.sync_session, "after_transaction_end")
    def _end_savepoint(sess, trans):
        # Reopen a SAVEPOINT if the endpoint committed the nested one.
        if trans.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
async def client(db_session):
    """Create test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Remove BaseHTTPMiddleware during tests. These middlewares internally
    # schedule tasks with asyncio.ensure_future on the default event loop,
    # which conflicts with the session-scoped test loop used by asyncpg.
    from starlette.middleware.base import BaseHTTPMiddleware

    original_middleware = [m for m in app.user_middleware]
    app.user_middleware = [
        m
        for m in app.user_middleware
        if not (hasattr(m.cls, "__mro__") and BaseHTTPMiddleware in m.cls.__mro__)
    ]
    app.middleware_stack = None  # force rebuild

    async with AsyncClient(app=app, base_url="http://localhost") as ac:
        yield ac

    app.dependency_overrides.clear()
    app.user_middleware = original_middleware
    app.middleware_stack = None


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
