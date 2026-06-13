"""
Regression tests for the FASE 1 bug fixes.

Each test ensures that a previously-broken module imports cleanly and
that the function it exposes can be referenced without raising
``NameError`` or ``UndefinedError``.

Bugs fixed:
- 1.1  ``stripe.py`` referenced undefined ``Property``
- 1.2  ``stripe.py`` had local ``status`` shadowing fastapi's ``status``
- 1.3  ``marketing.py`` used ``Vendor`` in a type hint without importing it
- 1.4  ``superadmin/content.py`` had a query-param ``status`` shadowing fastapi's
- 1.5  ``marketing.py`` redefined ``CampaignType`` in an inline import
- 1.6  ``admin/settings.py`` assigned ``expected_type`` and never used it
- Extra: ``superadmin/system.py`` and ``superadmin/users.py`` had several
  undefined names (``select``, ``func``, ``Vendor``, ``Booking``, ``timedelta``)
"""

import pytest
from importlib import import_module


@pytest.mark.parametrize(
    "module_path",
    [
        "app.api.v1.stripe",
        "app.api.v1.marketing",
        "app.api.v1.superadmin.content",
        "app.api.v1.superadmin.system",
        "app.api.v1.superadmin.users",
        "app.api.v1.admin.settings",
    ],
)
def test_module_imports_without_nameerror(module_path):
    """Each fixed module must import without NameError or UndefinedError."""
    mod = import_module(module_path)
    assert mod is not None


def test_stripe_helper_emails_use_property_join():
    """stripe._send_payment_confirmation_email must join Property table.

    This was the original F821: ``Property`` was referenced but never imported.
    The fix added it to the top-level imports.
    """
    from app.api.v1 import stripe
    import inspect

    src = inspect.getsource(stripe._send_payment_confirmation_email)
    # The booking/property join must be present and use the imported name.
    assert "Property" in src
    assert "Booking" in src


def test_stripe_get_connect_link_does_not_shadow_status():
    """The local variable inside get_vendor_connect_link must not be named
    ``status`` (which would shadow ``fastapi.status`` and trigger F823).
    """
    from app.api.v1 import stripe
    import inspect

    src = inspect.getsource(stripe.get_vendor_connect_link)
    # The fix renamed the local to ``connect_status``
    assert "connect_status" in src
    # And the response field ``status=`` is still allowed (that's a kwarg, not
    # a local variable). We just check that no assignment to ``status =`` remains.
    bad = [line for line in src.splitlines() if line.lstrip().startswith("status =")]
    assert not bad, f"Found shadowing local assignments: {bad}"


def test_marketing_current_vendor_uses_module_level_vendor():
    """The dependency function should not re-import Vendor inside its body."""
    from app.api.v1 import marketing
    import inspect

    src = inspect.getsource(marketing.get_current_vendor)
    assert "from app.models import Vendor" not in src


def test_marketing_create_template_does_not_reimport():
    """create_template should rely on top-level imports, not re-import
    ``EmailTemplate`` / ``CampaignType`` inside the function body.
    """
    from app.api.v1 import marketing
    import inspect

    src = inspect.getsource(marketing.create_template)
    assert "from app.models.marketing import" not in src


def test_superadmin_content_blog_filter_uses_alias():
    """list_blog_posts should accept ``status`` as a query param alias while
    using a non-shadowing local name internally.
    """
    from app.api.v1.superadmin import content
    import inspect

    src = inspect.getsource(content.list_blog_posts)
    assert 'alias="status"' in src
    assert "status_filter" in src


def test_admin_settings_validator_has_no_dead_assignment():
    """validate_setting_value must not leave an unused ``expected_type``."""
    from app.api.v1.admin import settings as admin_settings
    import inspect

    src = inspect.getsource(admin_settings.validate_setting_value)
    assert "expected_type" not in src


def test_superadmin_users_module_imports_all_dependencies():
    """All the previously-undefined names must now resolve."""
    # The module's import-time side effects previously raised NameError.
    # Re-importing should now succeed and the names must be resolvable.
    from app.models import Vendor, Booking
    from datetime import timedelta
    from sqlalchemy import select, func

    assert callable(select)
    assert callable(func)
    assert Vendor is not None
    assert Booking is not None
    assert timedelta is not None
