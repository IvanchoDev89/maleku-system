"""
Boat Equipment API - Náutico
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.utils import escape_like_pattern
from app.models import User, UserRole, Vendor, BoatEquipment, BoatType
from app.schemas import boat as boat_schema

router = APIRouter()


@router.get("/", response_model=list[boat_schema.BoatEquipmentResponse])
async def list_boats(
    location: str | None = None,
    equipment_type: BoatType | None = None,
    capacity: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[boat_schema.BoatEquipmentResponse]:
    """
    List all available boat and nautical equipment with filters.
    
    Args:
        location: Filter by location (partial match)
        equipment_type: Type of equipment (boat, jet ski, kayak, etc.)
        capacity: Minimum passenger capacity
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of boat equipment matching the filters
    """
    query = select(BoatEquipment).where(BoatEquipment.is_active, BoatEquipment.is_available)
    
    if location:
        query = query.where(BoatEquipment.location.ilike(f"%{escape_like_pattern(location)}%"))
    if equipment_type:
        query = query.where(BoatEquipment.equipment_type == equipment_type)
    if capacity:
        query = query.where(BoatEquipment.capacity >= capacity)
    
    result = await db.execute(query.order_by(BoatEquipment.price_per_day))
    boats = result.scalars().all()
    
    return boats


@router.get("/{boat_id}", response_model=boat_schema.BoatEquipmentDetailResponse)
async def get_boat(
    boat_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db)
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
    result = await db.execute(
        select(BoatEquipment).where(BoatEquipment.id == boat_id)
    )
    boat = result.scalar_one_or_none()
    
    if not boat:
        raise HTTPException(status_code=404, detail="Boat equipment not found")
    
    return boat


@router.post("/", response_model=boat_schema.BoatEquipmentResponse)
async def create_boat(
    boat_data: boat_schema.BoatEquipmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Create new boat equipment (Vendor only)"""
    result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=400, detail="Vendor profile not found")
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = ['equipment_type', 'brand', 'model', 'year', 'length', 'capacity',
                     'engine_type', 'engine_power', 'fuel_type', 'fuel_capacity', 'operating_area',
                     'equipment', 'daily_rate', 'weekly_rate', 'monthly_rate', 'security_deposit',
                     'description', 'photos', 'featured_photo', 'requirements', 'included_items',
                     'excluded_items', 'important_notes']
    boat_data_filtered = {k: v for k, v in boat_data.model_dump().items() if k in allowed_fields}
    
    boat = BoatEquipment(
        vendor_id=vendor.id,
        **boat_data_filtered
    )
    
    db.add(boat)
    await db.commit()
    await db.refresh(boat)
    
    return boat


@router.put("/{boat_id}", response_model=boat_schema.BoatEquipmentResponse)
async def update_boat(
    boat_id: uuid.UUID,
    boat_data: boat_schema.BoatEquipmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Update boat equipment (Owner only)"""
    result = await db.execute(
        select(BoatEquipment).where(BoatEquipment.id == boat_id)
    )
    boat = result.scalar_one_or_none()
    
    if not boat:
        raise HTTPException(status_code=404, detail="Boat equipment not found")
    
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = vendor_result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor profile required")

    if boat.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'equipment_type', 'brand', 'model', 'year', 'length', 'capacity',
                     'engine_type', 'engine_power', 'fuel_type', 'fuel_capacity', 'operating_area',
                     'equipment', 'daily_rate', 'weekly_rate', 'monthly_rate', 'security_deposit',
                     'description', 'photos', 'featured_photo', 'requirements', 'included_items',
                     'excluded_items', 'important_notes', 'is_active'}
    
    for key, value in boat_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(boat, key, value)
    
    boat.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(boat)
    
    return boat


@router.delete("/{boat_id}")
async def delete_boat(
    boat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Delete boat equipment (Owner only)"""
    result = await db.execute(
        select(BoatEquipment).where(BoatEquipment.id == boat_id)
    )
    boat = result.scalar_one_or_none()
    
    if not boat:
        raise HTTPException(status_code=404, detail="Boat equipment not found")
    
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
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
    current_user: User = Depends(require_role(UserRole.VENDOR))
):
    """Get vendor's own boat equipment"""
    result = await db.execute(
        select(Vendor).where(Vendor.user_id == current_user.id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        return []
    
    boats_result = await db.execute(
        select(BoatEquipment).where(BoatEquipment.vendor_id == vendor.id)
    )
    boats = boats_result.scalars().all()
    
    return boats