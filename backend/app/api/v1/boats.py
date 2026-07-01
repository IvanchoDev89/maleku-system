"""
Boat Equipment API - Náutico
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import get_current_user, require_role
from app.core.utils import escape_like_pattern
from app.models import BoatEquipment, BoatType, User, UserRole, Vendor
from app.schemas import boat as boat_schema

router = APIRouter(tags=["Boats"])


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


@router.get("", response_model=boat_schema.BoatEquipmentListResponse)
async def list_boats(
    location: str | None = None,
    equipment_type: BoatType | None = None,
    capacity: int | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> boat_schema.BoatEquipmentListResponse:
    """
    List all available boat and nautical equipment with filters and pagination.

    Args:
        location: Filter by location (partial match)
        equipment_type: Type of equipment (boat, jet ski, kayak, etc.)
        capacity: Minimum passenger capacity
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated list of boat equipment matching the filters
    """
    query = select(BoatEquipment).where(BoatEquipment.is_active, BoatEquipment.is_available)

    if location:
        query = query.where(BoatEquipment.location.ilike(f"%{escape_like_pattern(location)}%"))
    if equipment_type:
        query = query.where(BoatEquipment.equipment_type == equipment_type)
    if capacity:
        query = query.where(BoatEquipment.capacity >= capacity)

    count_query = (
        select(func.count())
        .select_from(BoatEquipment)
        .where(BoatEquipment.is_active, BoatEquipment.is_available)
    )
    if location:
        count_query = count_query.where(
            BoatEquipment.location.ilike(f"%{escape_like_pattern(location)}%")
        )
    if equipment_type:
        count_query = count_query.where(BoatEquipment.equipment_type == equipment_type)
    if capacity:
        count_query = count_query.where(BoatEquipment.capacity >= capacity)

    limit = min(limit, 100)
    result = await db.execute(query.order_by(BoatEquipment.price_per_day).offset(skip).limit(limit))
    boats = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return boat_schema.BoatEquipmentListResponse(
        items=boats,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{boat_id}", response_model=boat_schema.BoatEquipmentDetailResponse)
async def get_boat(
    boat_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> boat_schema.BoatEquipmentDetailResponse:
    """
    Get detailed information for a specific boat or nautical equipment.

    Args:
        boat_id: UUID of the equipment
        db: Database session

    Returns:
        Boat equipment details

    Raises:
        HTTPException: If equipment not found
    """
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    boat = result.scalar_one_or_none()

    if not boat:
        raise HTTPException(status_code=404, detail="Boat equipment not found")

    return boat


@router.post(
    "", response_model=boat_schema.BoatEquipmentResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
async def create_boat(
    request: Request,
    boat_data: boat_schema.BoatEquipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Create new boat equipment (Vendor only)"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor profile not found")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = [
        "equipment_type",
        "brand",
        "model",
        "year",
        "length",
        "capacity",
        "engine_type",
        "engine_power",
        "fuel_type",
        "fuel_capacity",
        "operating_area",
        "equipment",
        "daily_rate",
        "weekly_rate",
        "monthly_rate",
        "security_deposit",
        "description",
        "photos",
        "featured_photo",
        "requirements",
        "included_items",
        "excluded_items",
        "important_notes",
    ]
    boat_data_filtered = {k: v for k, v in boat_data.model_dump().items() if k in allowed_fields}

    boat = BoatEquipment(vendor_id=vendor.id, **boat_data_filtered)

    db.add(boat)
    await db.commit()
    await db.refresh(boat)

    return boat


@router.put("/{boat_id}", response_model=boat_schema.BoatEquipmentResponse)
@limiter.limit("10/minute")
async def update_boat(
    request: Request,
    boat_id: uuid.UUID,
    boat_data: boat_schema.BoatEquipmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Update boat equipment (Owner only)"""
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    boat = result.scalar_one_or_none()

    if not boat:
        raise HTTPException(status_code=404, detail="Boat equipment not found")

    vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if boat.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {
        "equipment_type",
        "brand",
        "model",
        "year",
        "length",
        "capacity",
        "engine_type",
        "engine_power",
        "fuel_type",
        "fuel_capacity",
        "operating_area",
        "equipment",
        "daily_rate",
        "weekly_rate",
        "monthly_rate",
        "security_deposit",
        "description",
        "photos",
        "featured_photo",
        "requirements",
        "included_items",
        "excluded_items",
        "important_notes",
        "is_active",
    }

    for key, value in boat_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(boat, key, value)

    boat.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(boat)

    return boat


@router.delete("/{boat_id}", response_model=DeleteResponse)
async def delete_boat(
    boat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Delete boat equipment (Owner only)"""
    result = await db.execute(select(BoatEquipment).where(BoatEquipment.id == boat_id))
    boat = result.scalar_one_or_none()

    if not boat:
        raise HTTPException(status_code=404, detail="Boat equipment not found")

    vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if boat.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    boat.is_active = False
    await db.commit()

    return {"message": "Boat equipment deleted"}


@router.get("/vendor/my-boats", response_model=list[boat_schema.BoatEquipmentResponse])
async def get_my_boats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
):
    """Get vendor's own boat equipment"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        return []

    boats_result = await db.execute(
        select(BoatEquipment).where(BoatEquipment.vendor_id == vendor.id)
    )
    boats = boats_result.scalars().all()

    return boats
