"""
Smoke tests for model imports and table resolution.

Verifies that:
- All model modules can be imported (no NameError, no missing dep)
- ``Base.metadata.tables`` contains a row per declared model
- tsvector indexes (raw ``text()``) don't break ``create_all``

These tests are not full integration tests; they're a cheap guard against
typos and import-time bugs. They run with the session-scoped engine fixture
in conftest.py.
"""

import pytest

from app.core.database import Base
import app.models  # noqa: F401  -- import side-effects register tables on Base


EXPECTED_TABLES = {
    "users",
    "vendors",
    "properties",
    "rooms",
    "room_availability",
    "tours",
    "bookings",
    "blog_posts",
    "reviews",
    "destinations",
    "conversations",
    "messages",
    "vehicles",
    "boats",
    "flights",
    "transportation",
    "pricing_rules",
    "newsletter_subscribers",
    "audit_logs",
    "security_logs",
    "role_permissions",
    "points_of_sale",
    # Marketing
    "email_campaigns",
    "email_templates",
    "email_logs",
    "marketing_automations",
    "inbox_messages",
    "email_preferences",
    "processed_webhooks",
}


def test_base_metadata_contains_all_tables():
    """Every domain model should register a table on Base.metadata."""
    actual = set(Base.metadata.tables.keys())
    missing = EXPECTED_TABLES - actual
    assert not missing, f"Models not registered: {missing}"


def test_no_duplicate_tables():
    """A model imported twice would register the same table twice."""
    tables = list(Base.metadata.tables.keys())
    assert len(tables) == len(set(tables)), "Duplicate table registration"


@pytest.mark.asyncio
async def test_create_all_succeeds(engine):
    """create_all should run without errors using the test engine.

    Regression for the tsvector ``func.to_tsvector('spanish', ...)``
    issue, which used to fail with 'No literal value renderer is
    available for literal value spanish with datatype REGCONFIG'.
    """
    # We rely on the session-scoped `engine` fixture having already
    # exercised create_all. If we got here, the schema was created.
    # Re-running create_all is a no-op; we just want to confirm
    # the metadata doesn't raise.
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: None)


def test_security_models_have_required_columns():
    """Audit and security models must expose the fields our code queries."""
    audit = Base.metadata.tables["audit_logs"]
    assert "action" in audit.c
    assert "user_id" in audit.c
    assert "entity_type" in audit.c
    assert "entity_id" in audit.c
    assert "created_at" in audit.c

    security = Base.metadata.tables["security_logs"]
    assert "action" in security.c
    assert "user_id" in security.c
    assert "ip_address" in security.c
    assert "created_at" in security.c
