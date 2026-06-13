import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.core.utils import escape_like_pattern
from app.models import User, UserRole, Vendor
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class VendorListItem(BaseModel):
    id: str
    business_name: str
    business_slug: str
    business_type: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    is_verified: bool
    is_active: bool
    created_at: Optional[str] = None
    owner_name: Optional[str] = None


class VendorStatsResponse(BaseModel):
    total: int
    verified: int
    unverified: int
    active: int
    inactive: int
    by_business_type: dict


class VendorListResponse(BaseModel):
    items: list[VendorListItem]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool


class VendorDetailResponse(BaseModel):
    id: str
    business_name: str
    business_slug: str
    business_type: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    is_verified: bool
    is_active: bool
    created_at: Optional[str] = None
    owner_name: Optional[str] = None


class VendorUpdateResponse(BaseModel):
    message: str
    id: str


class VendorVerifyResponse(BaseModel):
    message: str
    is_verified: bool


class VendorActiveResponse(BaseModel):
    message: str
    is_active: bool


class VendorDeleteResponse(BaseModel):
    message: str


def require_admin():
    return require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN)


@router.get("", response_model=VendorListResponse)
async def list_vendors(
    limit: int = 20,
    offset: int = 0,
    search: str = "",
    business_type: str = "",
    is_verified: str = "",
    is_active: str = "",
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all vendors with filters, search, and pagination"""

    # Build base query
    query = select(Vendor, User).outerjoin(User, Vendor.user_id == User.id)
    count_query = select(func.count(Vendor.id))

    # Apply filters
    conditions = []

    if search:
        safe_search = escape_like_pattern(search)
        search_term = f"%{safe_search}%"
        conditions.append(
            or_(
                Vendor.business_name.ilike(search_term),
                Vendor.business_slug.ilike(search_term),
            )
        )

    if business_type:
        conditions.append(Vendor.business_type == business_type)

    if is_verified == "true":
        conditions.append(Vendor.is_verified)
    elif is_verified == "false":
        conditions.append(Vendor.is_verified == False)

    if is_active == "true":
        conditions.append(Vendor.is_active)
    elif is_active == "false":
        conditions.append(Vendor.is_active == False)

    if conditions:
        query = query.where(*conditions)
        count_query = count_query.where(*conditions)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    sort_column = getattr(Vendor, sort_by, Vendor.created_at)
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    # Build response
    items = []
    for row in rows:
        vendor = row[0]
        user = row[1] if row[1] is not None else None

        # SECURITY: Admin-safe vendor data - NO financial or PII
        items.append(
            {
                "id": str(vendor.id),
                "business_name": vendor.business_name,
                "business_slug": vendor.business_slug,
                "business_type": vendor.business_type,
                "description": vendor.description,
                "logo_url": vendor.logo_url,
                "cover_image": vendor.cover_image,
                "address": vendor.address,
                # SECURITY: Phone removed - prevents PII exposure
                # SECURITY: Email removed - prevents PII exposure
                "rating": vendor.rating,
                "total_reviews": vendor.total_reviews,
                # SECURITY: Financial data removed
                # commission_rate, stripe_account_id, stripe_connected excluded
                "is_verified": vendor.is_verified,
                "is_active": vendor.is_active,
                "created_at": vendor.created_at.isoformat()
                if vendor.created_at
                else None,
                # SECURITY: Owner info limited to name only
                "owner_name": user.full_name if user else None,
            }
        )

    total_pages = (total + limit - 1) // limit if limit > 0 else 0

    return {
        "items": items,
        "total": total,
        "page": (offset // limit) + 1 if limit > 0 else 1,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": offset + limit < total if limit > 0 else False,
        "has_prev": offset > 0,
    }


@router.get("/stats/summary", response_model=VendorStatsResponse)
async def get_vendor_stats(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(require_admin)
):
    """Get vendor statistics"""

    # Total vendors
    total_result = await db.execute(select(func.count(Vendor.id)))
    total = total_result.scalar() or 0

    # Verified
    verified_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.is_verified)
    )
    verified = verified_result.scalar() or 0

    # Active
    active_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.is_active)
    )
    active = active_result.scalar() or 0

    # By business type
    type_result = await db.execute(
        select(Vendor.business_type, func.count(Vendor.id)).group_by(
            Vendor.business_type
        )
    )
    by_type = {row[0]: row[1] for row in type_result.all()}

    return {
        "total": total,
        "verified": verified,
        "unverified": total - verified,
        "active": active,
        "inactive": total - active,
        "by_business_type": by_type,
    }


@router.get("/{vendor_id}", response_model=VendorDetailResponse)
async def get_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get vendor details with owner info"""
    result = await db.execute(
        select(Vendor, User)
        .outerjoin(User, Vendor.user_id == User.id)
        .where(Vendor.id == vendor_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    vendor = row[0]
    user = row[1] if row[1] is not None else None

    # SECURITY: Admin-safe response - NO financial data or PII
    return {
        "id": str(vendor.id),
        "business_name": vendor.business_name,
        "business_slug": vendor.business_slug,
        "business_type": vendor.business_type,
        "description": vendor.description,
        "logo_url": vendor.logo_url,
        "cover_image": vendor.cover_image,
        "address": vendor.address,
        # SECURITY: PII removed - phone, email excluded
        "rating": vendor.rating,
        "total_reviews": vendor.total_reviews,
        # SECURITY: Financial data removed
        # commission_rate, stripe_account_id, stripe_connected excluded
        "is_verified": vendor.is_verified,
        "is_active": vendor.is_active,
        "created_at": vendor.created_at.isoformat() if vendor.created_at else None,
        # SECURITY: Owner info limited to name only - no email, phone, ID
        "owner_name": user.full_name if user else None,
    }


@router.put("/{vendor_id}", response_model=VendorUpdateResponse)
async def update_vendor(
    vendor_id: uuid.UUID,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update vendor details.

    SECURITY: Field whitelist prevents mass assignment.
    Admin CANNOT modify financial or sensitive fields.
    """
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    # SECURITY: Field whitelist - admin can only modify safe fields
    # Financial fields (commission_rate, stripe_account_id) EXCLUDED
    # Sensitive PII fields (phone, email) EXCLUDED
    allowed_fields = {
        "business_name",
        "business_slug",
        "business_type",
        "description",
        "logo_url",
        "cover_image",
        "address",
        "is_active",
        # NOTE: is_verified excluded - only Super Admin can verify
    }

    # SECURITY: Check for forbidden fields
    forbidden_fields = set(data.keys()) - allowed_fields
    if forbidden_fields:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot modify fields: {', '.join(forbidden_fields)}. Contact Super Admin.",
        )

    # Update only allowed fields
    for field, value in data.items():
        if hasattr(vendor, field):
            setattr(vendor, field, value)

    await db.flush()
    await db.refresh(vendor)
    await db.commit()

    return {"message": "Vendor updated successfully", "id": str(vendor.id)}


@router.put("/{vendor_id}/verify", response_model=VendorVerifyResponse)
async def verify_vendor(
    vendor_id: uuid.UUID,
    is_verified: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
):
    """Verify or unverify a vendor"""
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    vendor.is_verified = is_verified
    await db.flush()
    await db.commit()

    return {
        "message": f"Vendor {'verified' if is_verified else 'unverified'} successfully",
        "is_verified": vendor.is_verified,
    }


@router.put("/{vendor_id}/active", response_model=VendorActiveResponse)
async def toggle_vendor_active(
    vendor_id: uuid.UUID,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Activate or deactivate a vendor"""
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    vendor.is_active = is_active
    await db.flush()
    await db.commit()

    return {
        "message": f"Vendor {'activated' if is_active else 'deactivated'} successfully",
        "is_active": vendor.is_active,
    }


@router.delete("/{vendor_id}", response_model=VendorDeleteResponse)
async def delete_vendor(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
):
    """Soft delete a vendor (deactivate)"""
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    vendor.is_active = False
    await db.flush()
    await db.commit()

    return {"message": "Vendor deleted successfully"}
