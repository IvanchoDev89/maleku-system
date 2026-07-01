from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.core.utils import escape_like_pattern
from app.models import User, Vehicle, Boat as BoatEquipment, Flight, Transportation, Vendor
from app.models.vehicle import VehicleType as VehicleTypeEnum, TransmissionType, FuelType
from app.models.boat import BoatType as BoatTypeEnum
from app.models import TransportServiceType, PricingType as TransportationPricingType

router = APIRouter(prefix="/listings", tags=["Super Admin - Listings"])


# ==================== Vehicles ====================

@router.get("/vehicles", response_model=dict)
async def list_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    vehicle_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(Vehicle.id))
    query = select(Vehicle)

    if search:
        safe = escape_like_pattern(search)
        like = f"%{safe}%"
        query = query.where(
            (Vehicle.name.ilike(like)) | (Vehicle.model.ilike(like))
        )
        count_query = count_query.where(
            (Vehicle.name.ilike(like)) | (Vehicle.model.ilike(like))
        )

    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)
        count_query = count_query.where(Vehicle.vehicle_type == vehicle_type)

    if is_active is not None:
        query = query.where(Vehicle.is_active == is_active)
        count_query = count_query.where(Vehicle.is_active == is_active)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(Vehicle.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [
            {
                "id": str(v.id),
                "vendor_id": str(v.vendor_id) if v.vendor_id else None,
                "name": f"{v.brand} {v.model}",
                "brand": v.brand,
                "model": v.model,
                "vehicle_type": str(v.vehicle_type) if v.vehicle_type else None,
                "price_per_day": float(v.price_per_day or 0),
                "currency": v.currency or "USD",
                "is_active": v.is_active,
                "is_featured": v.is_featured,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
            for v in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/vehicles/{vehicle_id}", response_model=dict)
async def get_vehicle(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return {
        "id": str(v.id),
        "vendor_id": str(v.vendor_id) if v.vendor_id else None,
        "name": f"{v.brand} {v.model}",
        "brand": v.brand,
        "model": v.model,
        "vehicle_type": str(v.vehicle_type) if v.vehicle_type else None,
        "transmission": str(v.transmission) if v.transmission else None,
        "fuel_type": str(v.fuel_type) if v.fuel_type else None,
        "seats": v.seats,
        "year": v.year,
        "price_per_day": float(v.price_per_day or 0),
        "price_per_week": float(v.price_per_week or 0),
        "price_per_month": float(v.price_per_month or 0),
        "currency": v.currency or "USD",
        "images": v.images or [],
        "features": v.features or {},
        "is_active": v.is_active,
        "is_featured": v.is_featured,
        "location": v.location,
        "created_at": v.created_at.isoformat() if v.created_at else None,
        "updated_at": v.updated_at.isoformat() if v.updated_at else None,
    }


@router.post("/vehicles", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_vehicle(
    request: Request,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    vendor_id = data.get("vendor_id")
    if not vendor_id:
        raise HTTPException(status_code=400, detail="vendor_id is required")
    vendor_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    if not vendor_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vendor not found")

    allowed = {"vendor_id", "vehicle_type", "brand", "model", "year", "transmission",
               "fuel_type", "seats", "price_per_day", "price_per_week", "price_per_month",
               "currency", "features", "images", "location", "is_active"}
    create_data = {k: v for k, v in data.items() if k in allowed and v is not None}

    vehicle = Vehicle(**create_data)
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return {
        "success": True,
        "message": "Vehicle created",
        "id": str(vehicle.id),
    }


@router.patch("/vehicles/{vehicle_id}/activate", response_model=dict)
@limiter.limit("10/minute")
async def activate_vehicle(
    request: Request,
    vehicle_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    v.is_active = data.get("is_active", not v.is_active)
    await db.commit()
    return {"success": True, "is_active": v.is_active}


@router.put("/vehicles/{vehicle_id}", response_model=dict)
@limiter.limit("10/minute")
async def update_vehicle(
    request: Request,
    vehicle_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    allowed = {"name", "model", "description", "vehicle_type", "transmission",
               "fuel_type", "seats", "price_per_day", "currency", "images",
               "is_active", "is_featured"}
    for key, val in data.items():
        if key in allowed and val is not None:
            setattr(v, key, val)

    v.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "message": "Vehicle updated"}


@router.delete("/vehicles/{vehicle_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_vehicle(
    request: Request,
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    await db.delete(v)
    await db.commit()
    return {"success": True, "message": "Vehicle deleted"}


# ==================== Boats ====================

@router.get("/boats", response_model=dict)
async def list_boats(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    boat_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(BoatEquipment.id))
    query = select(BoatEquipment)

    if search:
        safe = escape_like_pattern(search)
        like = f"%{safe}%"
        query = query.where(BoatEquipment.name.ilike(like))
        count_query = count_query.where(BoatEquipment.name.ilike(like))

    if boat_type:
        query = query.where(BoatEquipment.boat_type == boat_type)
        count_query = count_query.where(BoatEquipment.boat_type == boat_type)

    if is_active is not None:
        query = query.where(BoatEquipment.is_active == is_active)
        count_query = count_query.where(BoatEquipment.is_active == is_active)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(BoatEquipment.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [
            {
                "id": str(b.id),
                "vendor_id": str(b.vendor_id) if b.vendor_id else None,
                "name": f"{b.brand or ''} {b.model or ''}".strip(),
                "brand": b.brand,
                "model": b.model,
                "equipment_type": str(b.equipment_type) if b.equipment_type else None,
                "capacity": b.capacity,
                "price_per_hour": float(b.price_per_hour or 0),
                "currency": b.currency or "USD",
                "is_active": b.is_active,
                "is_featured": b.is_featured,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/boats/{boat_id}", response_model=dict)
async def get_boat(
    boat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Boat not found")

    return {
        "id": str(b.id),
        "vendor_id": str(b.vendor_id) if b.vendor_id else None,
        "name": f"{b.brand or ''} {b.model or ''}".strip(),
        "brand": b.brand,
        "model": b.model,
        "equipment_type": str(b.equipment_type) if b.equipment_type else None,
        "capacity": b.capacity,
        "length_foot": float(b.length_foot) if b.length_foot else None,
        "price_per_hour": float(b.price_per_hour or 0),
        "price_per_day": float(b.price_per_day or 0),
        "price_per_week": float(b.price_per_week or 0),
        "currency": b.currency or "USD",
        "images": b.images or [],
        "features": b.features or {},
        "location": b.location,
        "is_active": b.is_active,
        "is_featured": b.is_featured,
        "created_at": b.created_at.isoformat() if b.created_at else None,
        "updated_at": b.updated_at.isoformat() if b.updated_at else None,
    }


@router.post("/boats", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_boat(
    request: Request,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    vendor_id = data.get("vendor_id")
    if not vendor_id:
        raise HTTPException(status_code=400, detail="vendor_id is required")
    vendor_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    if not vendor_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vendor not found")

    allowed = {"vendor_id", "equipment_type", "brand", "model", "year", "capacity",
               "length_foot", "features", "images", "price_per_hour", "price_per_day",
               "price_per_week", "currency", "requires_license", "license_notes",
               "location", "operating_area", "is_active"}
    create_data = {k: v for k, v in data.items() if k in allowed and v is not None}

    boat = BoatEquipment(**create_data)
    db.add(boat)
    await db.commit()
    await db.refresh(boat)
    return {
        "success": True,
        "message": "Boat created",
        "id": str(boat.id),
    }


@router.patch("/boats/{boat_id}/activate", response_model=dict)
@limiter.limit("10/minute")
async def activate_boat(
    request: Request,
    boat_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Boat not found")
    b.is_active = data.get("is_active", not b.is_active)
    await db.commit()
    return {"success": True, "is_active": b.is_active}


@router.put("/boats/{boat_id}", response_model=dict)
@limiter.limit("10/minute")
async def update_boat(
    request: Request,
    boat_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Boat not found")

    allowed = {"name", "description", "boat_type", "capacity", "length",
               "price_per_hour", "price_per_day", "currency", "images",
               "is_active", "is_featured"}
    for key, val in data.items():
        if key in allowed and val is not None:
            setattr(b, key, val)

    b.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "message": "Boat updated"}


@router.delete("/boats/{boat_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_boat(
    request: Request,
    boat_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    b = result.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Boat not found")
    await db.delete(b)
    await db.commit()
    return {"success": True, "message": "Boat deleted"}


# ==================== Flights ====================

@router.get("/flights", response_model=dict)
async def list_flights(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(Flight.id))
    query = select(Flight)

    if is_active is not None:
        query = query.where(Flight.is_active == is_active)
        count_query = count_query.where(Flight.is_active == is_active)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(Flight.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [
            {
                "id": str(f.id),
                "vendor_id": str(f.vendor_id) if f.vendor_id else None,
                "airline": f.airline,
                "flight_number": f.flight_number,
                "origin": f.origin,
                "destination": f.destination,
                "route_type": f.route_type,
                "price": float(f.price or 0),
                "currency": f.currency or "USD",
                "is_active": f.is_active,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/flights/{flight_id}", response_model=dict)
async def get_flight(
    flight_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Flight).where(Flight.id == flight_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="Flight not found")

    return {
        "id": str(f.id),
        "vendor_id": str(f.vendor_id) if f.vendor_id else None,
        "airline": f.airline,
        "flight_number": f.flight_number,
        "origin": f.origin,
        "destination": f.destination,
        "departure_time": f.departure_time.isoformat() if f.departure_time else None,
        "arrival_time": f.arrival_time.isoformat() if f.arrival_time else None,
        "route_type": f.route_type,
        "price": float(f.price or 0),
        "currency": f.currency or "USD",
        "is_active": f.is_active,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }


@router.put("/flights/{flight_id}", response_model=dict)
@limiter.limit("10/minute")
async def update_flight(
    request: Request,
    flight_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Flight).where(Flight.id == flight_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="Flight not found")

    allowed = {"airline", "flight_number", "origin", "destination",
               "departure_time", "arrival_time", "route_type",
               "price", "currency", "is_active"}
    for key, val in data.items():
        if key in allowed and val is not None:
            setattr(f, key, val)

    f.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "message": "Flight updated"}


@router.post("/flights", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_flight(
    request: Request,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    allowed = {"airline", "flight_number", "origin", "destination",
               "departure_time", "arrival_time", "route_type",
               "price", "currency", "is_active"}
    create_data = {k: v for k, v in data.items() if k in allowed and v is not None}

    flight = Flight(**create_data)
    db.add(flight)
    await db.commit()
    await db.refresh(flight)
    return {
        "success": True,
        "message": "Flight created",
        "id": str(flight.id),
    }


@router.delete("/flights/{flight_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_flight(
    request: Request,
    flight_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Flight).where(Flight.id == flight_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404, detail="Flight not found")
    await db.delete(f)
    await db.commit()
    return {"success": True, "message": "Flight deleted"}


# ==================== Transportation ====================

@router.get("/transportation", response_model=dict)
async def list_transportation(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(Transportation.id))
    query = select(Transportation)

    if service_type:
        query = query.where(Transportation.service_type == service_type)
        count_query = count_query.where(Transportation.service_type == service_type)

    if is_active is not None:
        query = query.where(Transportation.is_active == is_active)
        count_query = count_query.where(Transportation.is_active == is_active)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(Transportation.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [
            {
                "id": str(t.id),
                "vendor_id": str(t.vendor_id) if t.vendor_id else None,
                "name": t.name,
                "service_type": str(t.service_type) if t.service_type else None,
                "vehicle_type": t.vehicle_type,
                "origin": t.origin,
                "destination": t.destination,
                "price": float(t.price or 0),
                "currency": t.currency or "USD",
                "pricing_type": str(t.pricing_type) if t.pricing_type else None,
                "is_active": t.is_active,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/transportation/{transport_id}", response_model=dict)
async def get_transportation(
    transport_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transportation not found")

    return {
        "id": str(t.id),
        "vendor_id": str(t.vendor_id) if t.vendor_id else None,
        "name": t.name,
        "description": t.description,
        "service_type": str(t.service_type) if t.service_type else None,
        "vehicle_type": t.vehicle_type,
        "origin": t.origin,
        "destination": t.destination,
        "price": float(t.price or 0),
        "currency": t.currency or "USD",
        "pricing_type": str(t.pricing_type) if t.pricing_type else None,
        "schedule": t.schedule,
        "is_active": t.is_active,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "updated_at": t.updated_at.isoformat() if t.updated_at else None,
    }


@router.post("/transportation", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_transportation(
    request: Request,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    vendor_id = data.get("vendor_id")
    if not vendor_id:
        raise HTTPException(status_code=400, detail="vendor_id is required")
    vendor_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    if not vendor_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vendor not found")

    allowed = {"vendor_id", "name", "description", "service_type", "vehicle_type",
               "origin", "destination", "price", "currency", "pricing_type",
               "schedule", "is_active"}
    create_data = {k: v for k, v in data.items() if k in allowed and v is not None}

    transport = Transportation(**create_data)
    db.add(transport)
    await db.commit()
    await db.refresh(transport)
    return {
        "success": True,
        "message": "Transportation created",
        "id": str(transport.id),
    }


@router.patch("/transportation/{transport_id}/activate", response_model=dict)
@limiter.limit("10/minute")
async def activate_transportation(
    request: Request,
    transport_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transportation not found")
    t.is_active = data.get("is_active", not t.is_active)
    await db.commit()
    return {"success": True, "is_active": t.is_active}


@router.put("/transportation/{transport_id}", response_model=dict)
@limiter.limit("10/minute")
async def update_transportation(
    request: Request,
    transport_id: UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transportation not found")

    allowed = {"name", "description", "service_type", "vehicle_type",
               "origin", "destination", "price", "currency",
               "pricing_type", "schedule", "is_active"}
    for key, val in data.items():
        if key in allowed and val is not None:
            setattr(t, key, val)

    t.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "message": "Transportation updated"}


@router.delete("/transportation/{transport_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_transportation(
    request: Request,
    transport_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transportation not found")
    await db.delete(t)
    await db.commit()
    return {"success": True, "message": "Transportation deleted"}
