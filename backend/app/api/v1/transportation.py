"""
Transportation API - Transporte Privado
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models import User, UserRole, Vendor
from app.models import Transportation, TransportServiceType
from app.schemas import transportation as transportation_schema

router = APIRouter()


@router.get("/", response_model=list[transportation_schema.TransportationResponse])
async def list_transportation(
    location: str | None = None,
    service_type: TransportServiceType | None = None,
    capacity: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[transportation_schema.TransportationResponse]:
    """
    List all available private transportation services with filters.
    
    Args:
        location: Filter by service location
        service_type: Type of service (airport_transfer, city_tour, custom_route)
        capacity: Minimum passenger capacity
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of transportation services matching the filters
    
    TODO: Implementar búsqueda por ubicación con geolocalización
    """
    query = select(Transportation).where(Transportation.is_active, Transportation.is_available)
    
    if location:
        query = query.where(Transportation.locations.contains(location))
    if service_type:
        query = query.where(Transportation.service_type == service_type)
    if capacity:
        query = query.where(Transportation.capacity >= capacity)
    
    result = await db.execute(query.order_by(Transportation.base_price))
    services = result.scalars().all()
    
    return services


@router.get("/{transport_id}", response_model=transportation_schema.TransportationDetailResponse)
async def get_transportation(
    transport_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
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
    result = await db.execute(
        select(Transportation).where(Transportation.id == transport_id)
    )
    transport = result.scalar_one_or_none()
    
    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")
    
    return transport


@router.post("/", response_model=transportation_schema.TransportationResponse)
async def create_transportation(
    transport_data: transportation_schema.TransportationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Create new transportation service (Vendor only)"""
    result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor profile not found")
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = ['service_type', 'vehicle_type', 'vehicle_description', 'max_passengers',
                     'luggage_capacity', 'includes_driver', 'price_per_km', 'price_per_hour',
                     'minimum_hours', 'base_price', 'currency', 'operating_area', 'availability_hours',
                     'advance_booking_required', 'cancellation_policy', 'photos', 'requirements']
    transport_data_filtered = {k: v for k, v in transport_data.model_dump().items() if k in allowed_fields}
    
    transport = Transportation(
        vendor_id=vendor.id,
        **transport_data_filtered
    )
    
    db.add(transport)
    await db.commit()
    await db.refresh(transport)
    
    return transport


@router.put("/{transport_id}", response_model=transportation_schema.TransportationResponse)
async def update_transportation(
    transport_id: uuid.UUID,
    transport_data: transportation_schema.TransportationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Update transportation service (Owner only)"""
    result = await db.execute(
        select(Transportation).where(Transportation.id == transport_id)
    )
    transport = result.scalar_one_or_none()
    
    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")
    
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if transport.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'service_type', 'vehicle_type', 'vehicle_description', 'max_passengers',
                     'luggage_capacity', 'includes_driver', 'price_per_km', 'price_per_hour',
                     'minimum_hours', 'base_price', 'currency', 'operating_area', 'availability_hours',
                     'advance_booking_required', 'cancellation_policy', 'photos', 'requirements', 'is_active'}
    
    for key, value in transport_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(transport, key, value)
    
    transport.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(transport)
    
    return transport


@router.delete("/{transport_id}")
async def delete_transportation(
    transport_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Delete transportation service (Owner only)"""
    result = await db.execute(
        select(Transportation).where(Transportation.id == transport_id)
    )
    transport = result.scalar_one_or_none()
    
    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")
    
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if transport.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    transport.is_active = False
    await db.commit()
    
    return {"message": "Transportation service deleted"}


@router.get("/vendor/my-transports", response_model=list[transportation_schema.TransportationResponse])
async def get_my_transportation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Get vendor's own transportation services"""
    result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        return []
    
    transports_result = await db.execute(
        select(Transportation).where(Transportation.vendor_id == vendor.id)
    )
    transports = transports_result.scalars().all()
    
    return transports


@router.post("/calculate-price")
async def calculate_price(
    transport_id: uuid.UUID,
    distance_km: float,
    duration_hours: float = None,
    db: AsyncSession = Depends(get_db)
):
    """Calculate transportation price"""
    result = await db.execute(
        select(Transportation).where(Transportation.id == transport_id)
    )
    transport = result.scalar_one_or_none()
    
    if not transport:
        raise HTTPException(status_code=404, detail="Transportation service not found")
    
    from app.models import PricingType
    
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
        "currency": "USD"
    }