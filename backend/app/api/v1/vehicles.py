"""
Vehicles API - Rent a Car
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.utils import escape_like_pattern
from app.models import User, UserRole, Vendor, Vehicle, VehicleType
from app.schemas import vehicle as vehicle_schema
from pydantic import BaseModel

router = APIRouter()


class DeleteResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str


class MarkReadResponse(BaseModel):
    message: str
    conversation_id: str


class ReorderResponse(BaseModel):
    message: str
    items_updated: int


class ActivateResponse(BaseModel):
    message: str
    is_active: bool


class ChangeRoleResponse(BaseModel):
    message: str
    user_id: str
    new_role: str


class VerifyResponse(BaseModel):
    message: str
    is_verified: bool


class ToggleActiveResponse(BaseModel):
    message: str
    is_active: bool


class PresignedUrlResponse(BaseModel):
    url: str
    expires_in: int
    fields: dict


@router.get("", response_model=list[vehicle_schema.VehicleResponse])
async def list_vehicles(
    location: str | None = None,
    vehicle_type: VehicleType | None = None,
    seats: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[vehicle_schema.VehicleResponse]:
    """
    List all available vehicles with optional filters.

    Args:
        location: Filter by location (partial match)
        vehicle_type: Filter by vehicle type (car, suv, van, etc.)
        seats: Minimum seating capacity
        db: Database session
        current_user: Authenticated user

    Returns:
        List of vehicles matching the filters
    """
    query = select(Vehicle).where(Vehicle.is_active, Vehicle.is_available)

    if location:
        query = query.where(
            Vehicle.location.ilike(f"%{escape_like_pattern(location)}%")
        )
    if vehicle_type:
        query = query.where(Vehicle.vehicle_type == vehicle_type)
    if seats:
        query = query.where(Vehicle.seats >= seats)

    result = await db.execute(query.order_by(Vehicle.price_per_day))
    vehicles = result.scalars().all()

    return vehicles


@router.get("/{vehicle_id}", response_model=vehicle_schema.VehicleDetailResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> vehicle_schema.VehicleDetailResponse:
    """
    Get detailed information for a specific vehicle.

    Args:
        vehicle_id: UUID of the vehicle
        db: Database session

    Returns:
        Vehicle details

    Raises:
        HTTPException: If vehicle not found
    """
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle


@router.post("", response_model=vehicle_schema.VehicleResponse)
async def create_vehicle(
    vehicle_data: vehicle_schema.VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Create a new vehicle (Vendor only)"""
    # Get vendor profile
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor profile not found")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = [
        "vehicle_type",
        "brand",
        "model",
        "year",
        "color",
        "license_plate",
        "capacity",
        "transmission",
        "fuel_type",
        "features",
        "daily_rate",
        "weekly_rate",
        "monthly_rate",
        "security_deposit",
        "description",
        "photos",
        "is_insured",
        "insurance_details",
        "requirements",
    ]
    vehicle_data_filtered = {
        k: v for k, v in vehicle_data.model_dump().items() if k in allowed_fields
    }

    vehicle = Vehicle(vendor_id=vendor.id, **vehicle_data_filtered)

    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    return vehicle


@router.put("/{vehicle_id}", response_model=vehicle_schema.VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    vehicle_data: vehicle_schema.VehicleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Update vehicle (Owner only)"""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verify ownership
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if vehicle.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {
        "vehicle_type",
        "brand",
        "model",
        "year",
        "color",
        "license_plate",
        "capacity",
        "transmission",
        "fuel_type",
        "features",
        "daily_rate",
        "weekly_rate",
        "monthly_rate",
        "security_deposit",
        "description",
        "photos",
        "is_insured",
        "insurance_details",
        "requirements",
        "is_active",
    }

    for key, value in vehicle_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(vehicle, key, value)

    vehicle.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(vehicle)

    return vehicle


@router.delete("/{vehicle_id}", response_model=DeleteResponse)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Delete vehicle (Owner only)"""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verify ownership
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if vehicle.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    vehicle.is_active = False
    await db.commit()

    return {"message": "Vehicle deleted"}


@router.get("/vendor/my-vehicles", response_model=list[vehicle_schema.VehicleResponse])
async def get_my_vehicles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Get vendor's own vehicles"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        return []

    vehicles_result = await db.execute(
        select(Vehicle).where(Vehicle.vendor_id == vendor.id)
    )
    vehicles = vehicles_result.scalars().all()

    return vehicles
