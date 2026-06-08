import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models import User, UserRole, Vendor, Property, Tour, Booking, BookingStatus
from app.schemas import VendorResponse, VendorUpdate, VendorPublicResponse
from app.services.cache_service import cache

router = APIRouter()

CACHE_TTL_LIST = 300  # 5 minutes for vendor lists
CACHE_TTL_DETAIL = 600  # 10 minutes for vendor details


@router.get("", response_model=list[VendorPublicResponse])
async def get_vendors(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    cache_key = f"vendors:list:{limit}:{offset}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return [VendorPublicResponse(**item) for item in cached]
    
    result = await db.execute(
        select(Vendor)
        .where(Vendor.is_active)
        .order_by(Vendor.rating.desc())
        .offset(offset)
        .limit(limit)
    )
    vendors = result.scalars().all()
    response = [VendorPublicResponse.model_validate(v) for v in vendors]
    
    # Cache the response
    await cache.set(cache_key, [item.model_dump() for item in response], ttl=CACHE_TTL_LIST, tags=["vendors"])
    
    return response


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"vendors:detail:{vendor_id}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return VendorResponse(**cached)
    
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    response = VendorResponse.model_validate(vendor)
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["vendors", f"vendor:{vendor_id}"])
    
    return response


@router.get("/slug/{slug}", response_model=VendorResponse)
async def get_vendor_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"vendors:slug:{slug}"
    
    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return VendorResponse(**cached)
    
    result = await db.execute(select(Vendor).where(Vendor.business_slug == slug))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    response = VendorResponse.model_validate(vendor)
    await cache.set(cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["vendors", f"vendor:{vendor.id}"])
    
    return response


@router.get("/me/profile", response_model=VendorResponse)
async def get_my_vendor_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource"
        )
    
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    return VendorResponse.model_validate(vendor)


@router.put("/me/profile", response_model=VendorResponse)
async def update_my_vendor_profile(
    data: VendorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource"
        )
    
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'business_name', 'description', 'phone', 'address', 'city', 
                     'country', 'website', 'logo_url', 'tax_id'}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in allowed_fields:
            setattr(vendor, field, value)
    
    await db.flush()
    await db.commit()

    # Invalidate vendor caches
    await cache.delete(f"vendors:detail:{vendor.id}")
    await cache.delete(f"vendors:slug:{vendor.business_slug}")
    await cache.invalidate_tag("vendors")

    return VendorResponse.model_validate(vendor)


@router.get("/me/analytics")
async def get_my_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource"
        )
    
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor profile not found"
        )
    
    # Get property count
    prop_result = await db.execute(
        select(func.count()).where(Property.vendor_id == vendor.id)
    )
    total_properties = prop_result.scalar()

    tour_result = await db.execute(
        select(func.count()).where(Tour.vendor_id == vendor.id)
    )
    total_tours = tour_result.scalar()

    # Get bookings (still need full rows for aggregation)
    booking_result = await db.execute(
        select(Booking).where(Booking.vendor_id == vendor.id)
    )
    bookings = booking_result.scalars().all()
    
    pending = sum(1 for b in bookings if b.status == BookingStatus.PENDING)
    confirmed = sum(1 for b in bookings if b.status == BookingStatus.CONFIRMED)
    completed = sum(1 for b in bookings if b.status == BookingStatus.COMPLETED)
    total_revenue = sum(b.total_amount for b in bookings if b.status == BookingStatus.COMPLETED)
    
    return {
        "total_properties": total_properties,
        "total_tours": total_tours,
        "total_bookings": len(bookings),
        "pending_bookings": pending,
        "confirmed_bookings": confirmed,
        "completed_bookings": completed,
        "total_revenue": total_revenue,
        "rating": vendor.rating,
        "total_reviews": vendor.total_reviews,
        "commission_rate": vendor.commission_rate
    }


@router.put("/{vendor_id}/verify")
async def verify_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    vendor.is_verified = True
    await db.flush()
    await db.commit()

    # Invalidate vendor caches
    await cache.delete(f"vendors:detail:{vendor.id}")
    await cache.delete(f"vendors:slug:{vendor.business_slug}")
    await cache.invalidate_tag("vendors")

    return {"message": "Vendor verified successfully"}


@router.put("/{vendor_id}/activate")
async def toggle_vendor_active(
    vendor_id: uuid.UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))
):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    vendor.is_active = is_active
    await db.flush()
    await db.commit()

    # Invalidate vendor caches
    await cache.delete(f"vendors:detail:{vendor.id}")
    await cache.delete(f"vendors:slug:{vendor.business_slug}")
    await cache.invalidate_tag("vendors")

    return {"message": f"Vendor {'activated' if is_active else 'deactivated'}"}