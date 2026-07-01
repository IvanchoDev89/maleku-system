"""
Transportation API - Transporte Privado
"""

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import get_current_user, require_role
from app.models import PricingType, Transportation, TransportServiceType, User, UserRole, Vendor
from app.schemas import transportation as transportation_schema

router = APIRouter(tags=["Transportation"])


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


@router.get("", response_model=list[transportation_schema.TransportationResponse])
async def list_transportation(
    location: str | None = None,
    service_type: TransportServiceType | None = None,
    capacity: int | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    List all available private transportation services with filters and pagination.

    Args:
        location: Filter by service location
        service_type: Type of service (airport_transfer, city_tour, custom_route)
        capacity: Minimum passenger capacity
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated list of transportation services matching the filters

    Note: Geolocation-based search not yet implemented
    """
    query = select(Transportation).where(Transportation.is_active, Transportation.is_available)

    if location:
        query = query.where(Transportation.locations.contains(location))
    if service_type:
        query = query.where(Transportation.service_type == service_type)
    if capacity:
        query = query.where(Transportation.capacity >= capacity)

    count_query = select(
        select(Transportation.id)
        .where(Transportation.is_active, Transportation.is_available)
        .subquery()
        .c.id
    )
    if location:
        count_query = count_query.where(Transportation.locations.contains(location))
    if service_type:
        count_query = count_query.where(Transportation.service_type == service_type)
    if capacity:
        count_query = count_query.where(Transportation.capacity >= capacity)

    limit = min(limit, 100)
    result = await db.execute(query.order_by(Transportation.base_price).offset(skip).limit(limit))
    services = result.scalars().all()

    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    return {
        "items": services,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{transport_id}", response_model=transportation_schema.TransportationDetailResponse)
async def get_transportation(
    transport_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> transportation_schema.TransportationDetailResponse:
    """
    Get detailed information for a specific transportation service.

    Args:
        transport_id: UUID of the transportation service
        db: Database session

    Returns:
        Transportation service details

    Raises:
        HTTPException: If service not found
    """
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    transport = result.scalar_one_or_none()

    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")

    return transport


@router.post(
    "",
    response_model=transportation_schema.TransportationResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def create_transportation(
    request: Request,
    transport_data: transportation_schema.TransportationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
) -> transportation_schema.TransportationResponse:
    """Create new transportation service (Vendor only)"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor profile not found")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = [
        "service_type",
        "vehicle_type",
        "vehicle_description",
        "max_passengers",
        "luggage_capacity",
        "includes_driver",
        "price_per_km",
        "price_per_hour",
        "minimum_hours",
        "base_price",
        "currency",
        "operating_area",
        "availability_hours",
        "advance_booking_required",
        "cancellation_policy",
        "photos",
        "requirements",
    ]
    transport_data_filtered = {
        k: v for k, v in transport_data.model_dump().items() if k in allowed_fields
    }

    transport = Transportation(vendor_id=vendor.id, **transport_data_filtered)

    db.add(transport)
    await db.commit()
    await db.refresh(transport)

    return transport


@router.put("/{transport_id}", response_model=transportation_schema.TransportationResponse)
@limiter.limit("10/minute")
async def update_transportation(
    request: Request,
    transport_id: uuid.UUID,
    transport_data: transportation_schema.TransportationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
) -> transportation_schema.TransportationResponse:
    """Update transportation service (Owner only)"""
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    transport = result.scalar_one_or_none()

    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")

    vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if transport.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {
        "service_type",
        "vehicle_type",
        "vehicle_description",
        "max_passengers",
        "luggage_capacity",
        "includes_driver",
        "price_per_km",
        "price_per_hour",
        "minimum_hours",
        "base_price",
        "currency",
        "operating_area",
        "availability_hours",
        "advance_booking_required",
        "cancellation_policy",
        "photos",
        "requirements",
        "is_active",
    }

    for key, value in transport_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(transport, key, value)

    transport.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(transport)

    return transport


@router.delete("/{transport_id}", response_model=DeleteResponse)
async def delete_transportation(
    transport_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
) -> dict:
    """Delete transportation service (Owner only)"""
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    transport = result.scalar_one_or_none()

    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")

    vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if transport.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    transport.is_active = False
    await db.commit()

    return {"message": "Transportation service deleted"}


@router.get(
    "/vendor/my-transports",
    response_model=list[transportation_schema.TransportationResponse],
)
async def get_my_transportation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR)),
) -> list[transportation_schema.TransportationResponse]:
    """Get vendor's own transportation services"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        return []

    transports_result = await db.execute(
        select(Transportation).where(Transportation.vendor_id == vendor.id)
    )
    transports = transports_result.scalars().all()

    return transports


@router.post("/calculate-price", response_model=dict)
@limiter.limit("30/minute")
async def calculate_price(
    transport_id: uuid.UUID,
    distance_km: float,
    duration_hours: float | None = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Calculate transportation price"""
    result = await db.execute(select(Transportation).where(Transportation.id == transport_id))
    transport = result.scalar_one_or_none()

    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")

    if transport.pricing_type == PricingType.PER_ROUTE:
        total = transport.base_price + (distance_km * transport.price_per_km)
    elif transport.pricing_type == PricingType.PER_HOUR and duration_hours:
        total = transport.base_price + (duration_hours * transport.price_per_hour)
    elif transport.pricing_type == PricingType.PER_DAY:
        total = transport.base_price
    else:
        total = transport.base_price

    return {
        "base_price": transport.base_price,
        "distance_km": distance_km,
        "duration_hours": duration_hours,
        "total_price": round(total, 2),
        "currency": "USD",
    }
