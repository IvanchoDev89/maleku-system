"""
Tests for BOLA-vendor-None crash protection (OWASP API1:2023).

Verifies that a VENDOR-role user WITHOUT a Vendor profile gets a clean 403
(not a 500/AttributeError) when trying to update or delete a resource.
"""
import pytest
import uuid

from app.models import Tour, Property, Vehicle, BoatEquipment, Transportation

pytestmark = pytest.mark.security


async def _make_resource(db_session, model, vendor_id):
    """Insert a minimum resource tied to vendor_id for the test."""
    obj = model()
    # Set vendor_id if the model has it
    if hasattr(obj, "vendor_id"):
        obj.vendor_id = vendor_id
    # Required enums/strings vary by model; use minimal valid state
    if model is Tour:
        obj.name = "Test Tour"
        obj.slug = f"test-tour-{uuid.uuid4().hex[:8]}"
        obj.price = 100.0
        obj.currency = "USD"
        obj.is_active = True
    elif model is Property:
        obj.name = "Test Property"
        obj.slug = f"test-prop-{uuid.uuid4().hex[:8]}"
        obj.property_type = "hotel"
        obj.is_active = True
    elif model is Vehicle:
        obj.brand = "Toyota"
        obj.model = "Corolla"
        obj.year = 2020
        obj.license_plate = f"TEST-{uuid.uuid4().hex[:6]}"
        obj.vehicle_type = "car"
        obj.transmission = "automatic"
        obj.fuel_type = "gasoline"
        obj.daily_rate = 50.0
        obj.is_active = True
    elif model is BoatEquipment:
        obj.brand = "Yamaha"
        obj.model = "242"
        obj.year = 2020
        obj.equipment_type = "boat"
        obj.fuel_type = "gasoline"
        obj.daily_rate = 200.0
        obj.is_active = True
    elif model is Transportation:
        obj.service_type = "private"
        obj.vehicle_type = "sedan"
        obj.max_passengers = 4
        obj.price_per_km = 1.5
        obj.is_active = True
    db_session.add(obj)
    await db_session.commit()
    await db_session.refresh(obj)
    return obj


async def _other_vendor_id(db_session) -> uuid.UUID:
    """Create a vendor profile for 'someone else' and return its id."""
    from app.models import Vendor
    other = User(
        email=f"other-vendor-{uuid.uuid4().hex[:6]}@example.com",
        password_hash="x",
        full_name="Other Vendor",
        role=UserRole.VENDOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(other)
    await db_session.commit()
    await db_session.refresh(other)
    vendor = Vendor(
        user_id=other.id,
        business_name="Other Hotel",
        business_slug=f"other-{uuid.uuid4().hex[:8]}",
        business_type="hotel",
    )
    db_session.add(vendor)
    await db_session.commit()
    await db_session.refresh(vendor)
    return vendor.id


from app.models import User, UserRole  # noqa: E402


# ---------------------------------------------------------------------------
# Tours
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_update_tour(
    vendor_no_profile_client, db_session
):
    """VENDOR role without a Vendor profile must get 403, not 500 (AttributeError)."""
    other_vendor_id = await _other_vendor_id(db_session)
    tour = await _make_resource(db_session, Tour, other_vendor_id)

    resp = await vendor_no_profile_client.put(
        f"/api/v1/tours/{tour.id}",
        json={"name": "Hacked Tour"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_delete_tour(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    tour = await _make_resource(db_session, Tour, other_vendor_id)

    resp = await vendor_no_profile_client.delete(f"/api/v1/tours/{tour.id}")
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_update_property(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    prop = await _make_resource(db_session, Property, other_vendor_id)

    resp = await vendor_no_profile_client.put(
        f"/api/v1/properties/{prop.id}",
        json={"name": "Hacked Property"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_delete_property(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    prop = await _make_resource(db_session, Property, other_vendor_id)

    resp = await vendor_no_profile_client.delete(f"/api/v1/properties/{prop.id}")
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_update_vehicle(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    vehicle = await _make_resource(db_session, Vehicle, other_vendor_id)

    resp = await vendor_no_profile_client.put(
        f"/api/v1/vehicles/{vehicle.id}",
        json={"brand": "Hacked"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_delete_vehicle(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    vehicle = await _make_resource(db_session, Vehicle, other_vendor_id)

    resp = await vendor_no_profile_client.delete(f"/api/v1/vehicles/{vehicle.id}")
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


# ---------------------------------------------------------------------------
# Boats
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_update_boat(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    boat = await _make_resource(db_session, BoatEquipment, other_vendor_id)

    resp = await vendor_no_profile_client.put(
        f"/api/v1/boats/{boat.id}",
        json={"brand": "Hacked"},
    )
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_vendor_without_profile_cannot_delete_boat(
    vendor_no_profile_client, db_session
):
    other_vendor_id = await _other_vendor_id(db_session)
    boat = await _make_resource(db_session, BoatEquipment, other_vendor_id)

    resp = await vendor_no_profile_client.delete(f"/api/v1/boats/{boat.id}")
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}: {resp.text}"
