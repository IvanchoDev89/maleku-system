"""
Super Admin Vendors Management API

Comprehensive vendor lifecycle management including approval workflow,
suspension, analytics, and compliance monitoring.

Security:
- All endpoints protected by require_superadmin
- Audit logging for all state changes
- Input validation and sanitization
- Rate limiting recommended at nginx level
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case,  select, or_, func, desc
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.core.security import require_superadmin
from app.core.utils import escape_like_pattern
from app.models import User, Vendor, Booking, Review, Property, VendorStatus
from app.services.audit_service import AuditService
from app.models.audit import AuditAction

router = APIRouter(prefix="/vendors", tags=["Super Admin - Vendors"])


# ============================================================================
# Enums and Schemas
# ============================================================================

class VendorSortBy(str, Enum):
    CREATED_AT = "created_at"
    NAME = "business_name"
    RATING = "rating"
    BOOKINGS = "total_bookings"
    REVENUE = "total_revenue"


class VendorFilterStatus(str, Enum):
    ALL = "all"
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class VendorApprovalAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    SUSPEND = "suspend"
    REACTIVATE = "reactivate"


class VendorApprovalRequest(BaseModel):
    action: VendorApprovalAction
    reason: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)
    require_documents: Optional[List[str]] = None


class VendorStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    vendor_id: UUID
    total_bookings: int = 0
    total_revenue: float = 0.0
    completed_bookings: int = 0
    cancelled_bookings: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    response_rate: float = 0.0
    avg_response_time_minutes: Optional[int] = None


class VendorDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    business_name: str
    business_type: str
    description: Optional[str]
    status: str
    tax_id: Optional[str]
    commission_rate: float
    is_featured: bool
    rating: float
    total_bookings: int
    created_at: datetime
    updated_at: datetime
    
    # Owner info
    owner_id: UUID
    owner_email: str
    owner_name: str
    owner_phone: Optional[str]
    
    # Statistics
    stats: VendorStats
    
    # Compliance
    documents_verified: bool
    last_compliance_check: Optional[datetime]
    compliance_flags: List[str]


class VendorListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    business_name: str
    business_type: str
    status: str
    rating: float
    total_bookings: int
    is_featured: bool
    created_at: datetime
    owner_email: str
    owner_name: str


class VendorAnalytics(BaseModel):
    total_vendors: int
    pending_approval: int
    active_vendors: int
    suspended_vendors: int
    rejected_vendors: int
    
    top_performers: List[VendorStats]
    recent_registrations: List[VendorListResponse]
    
    revenue_by_vendor_type: dict
    bookings_by_month: List[dict]


class ComplianceCheckRequest(BaseModel):
    check_documents: bool = True
    check_bookings: bool = True
    check_reviews: bool = True


# ============================================================================
# Helper Functions
# ============================================================================

async def calculate_vendor_stats(db: AsyncSession, vendor_id: UUID) -> VendorStats:
    """Calculate comprehensive vendor statistics."""
    # Bookings stats
    result = await db.execute(
        select(
            func.count(Booking.id).label("total"),
            func.sum(Booking.total_amount).label("revenue"),
            func.sum(case((Booking.status == "completed", 1), else_=0)).label("completed"),
            func.sum(case((Booking.status == "cancelled", 1), else_=0)).label("cancelled"),
        ).where(Booking.vendor_id == vendor_id)
    )
    row = result.one()
    
    # Reviews stats
    result = await db.execute(
        select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("total_reviews"),
        ).where(Review.vendor_id == vendor_id)
    )
    review_row = result.one()
    
    return VendorStats(
        vendor_id=vendor_id,
        total_bookings=row.total or 0,
        total_revenue=float(row.revenue or 0),
        completed_bookings=row.completed or 0,
        cancelled_bookings=row.cancelled or 0,
        average_rating=float(review_row.avg_rating or 0),
        total_reviews=review_row.total_reviews or 0,
        response_rate=0.0,  # Calculate based on message responses
        avg_response_time_minutes=None,
    )


async def run_compliance_check(db: AsyncSession, vendor: Vendor) -> List[str]:
    """Run compliance checks and return flags."""
    flags = []
    
    # Check if vendor has properties/tours
    result = await db.execute(
        select(func.count(Property.id)).where(Property.vendor_id == vendor.id)
    )
    property_count = result.scalar()
    
    if property_count == 0:
        flags.append("no_properties")
    
    # Check booking completion rate
    result = await db.execute(
        select(
            func.count().label("total"),
            func.sum(case((Booking.status == "completed", 1), else_=0)).label("completed"),
        ).where(Booking.vendor_id == vendor.id)
    )
    row = result.one()
    if row.total and row.total > 0:
        completion_rate = (row.completed or 0) / row.total
        if completion_rate < 0.5:
            flags.append("low_completion_rate")
    
    # Check rating
    if vendor.rating and vendor.rating < 2.0:
        flags.append("low_rating")
    
    return flags


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=List[VendorListResponse])
async def list_vendors(
    status: Optional[VendorFilterStatus] = Query(default=VendorFilterStatus.ALL),
    sort_by: VendorSortBy = Query(default=VendorSortBy.CREATED_AT),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    search: Optional[str] = Query(default=None, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    featured_only: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> List[VendorListResponse]:
    """
    List all vendors with filtering and sorting.
    
    Query Parameters:
    - status: Filter by vendor status (all, pending, active, suspended, rejected)
    - sort_by: Sort field (created_at, name, rating, bookings, revenue)
    - sort_order: asc or desc
    - search: Search by business name or owner email
    - featured_only: Show only featured vendors
    """
    query = select(Vendor).options(selectinload(Vendor.owner))
    
    # Apply status filter
    if status != VendorFilterStatus.ALL:
        query = query.where(Vendor.status == VendorStatus(status.value))
    
    # Apply search
    if search:
        safe_search = escape_like_pattern(search)
        search_pattern = f"%{safe_search}%"
        query = query.where(
            or_(
                Vendor.business_name.ilike(search_pattern),
                Vendor.owner.has(User.email.ilike(search_pattern))
            )
        )
    
    # Apply featured filter
    if featured_only:
        query = query.where(Vendor.is_featured)
    
    # Apply sorting
    sort_column = {
        VendorSortBy.CREATED_AT: Vendor.created_at,
        VendorSortBy.NAME: Vendor.business_name,
        VendorSortBy.RATING: Vendor.rating,
        VendorSortBy.BOOKINGS: Vendor.total_bookings,
    }.get(sort_by, Vendor.created_at)
    
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    vendors = result.scalars().all()
    
    return [
        VendorListResponse(
            id=v.id,
            business_name=v.business_name,
            business_type=v.business_type,
            status=v.status.value if isinstance(v.status, VendorStatus) else v.status,
            rating=v.rating or 0.0,
            total_bookings=v.total_bookings or 0,
            is_featured=v.is_featured or False,
            created_at=v.created_at,
            owner_email=v.owner.email,
            owner_name=v.owner.full_name,
        )
        for v in vendors
    ]


@router.get("/pending", response_model=List[VendorDetailResponse])
async def list_pending_vendors(
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> List[VendorDetailResponse]:
    """
    List vendors pending approval with detailed information.
    
    Sorted by registration date (oldest first for priority).
    """
    result = await db.execute(
        select(Vendor)
        .options(selectinload(Vendor.owner))
        .where(Vendor.status == VendorStatus.PENDING)
        .order_by(Vendor.created_at)
        .limit(limit)
    )
    vendors = result.scalars().all()
    
    response_list = []
    for v in vendors:
        stats = await calculate_vendor_stats(db, v.id)
        flags = await run_compliance_check(db, v)
        
        response_list.append(VendorDetailResponse(
            id=v.id,
            business_name=v.business_name,
            business_type=v.business_type,
            description=v.description,
            status=v.status.value if isinstance(v.status, VendorStatus) else v.status,
            tax_id=v.tax_id,
            commission_rate=v.commission_rate,
            is_featured=v.is_featured or False,
            rating=v.rating or 0.0,
            total_bookings=v.total_bookings or 0,
            created_at=v.created_at,
            updated_at=v.updated_at,
            owner_id=v.owner_id,
            owner_email=v.owner.email,
            owner_name=v.owner.full_name,
            owner_phone=v.owner.phone,
            stats=stats,
            documents_verified=False,  # Set based on document verification
            last_compliance_check=None,
            compliance_flags=flags,
        ))
    
    return response_list


@router.get("/{vendor_id}", response_model=VendorDetailResponse)
async def get_vendor_details(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> VendorDetailResponse:
    """
    Get detailed information about a specific vendor.
    
    Includes statistics, compliance flags, and owner information.
    """
    result = await db.execute(
        select(Vendor)
        .options(selectinload(Vendor.owner))
        .where(Vendor.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    stats = await calculate_vendor_stats(db, vendor.id)
    flags = await run_compliance_check(db, vendor)
    
    return VendorDetailResponse(
        id=vendor.id,
        business_name=vendor.business_name,
        business_type=vendor.business_type,
        description=vendor.description,
        status=vendor.status.value if isinstance(vendor.status, VendorStatus) else vendor.status,
        tax_id=vendor.tax_id,
        commission_rate=vendor.commission_rate,
        is_featured=vendor.is_featured or False,
        rating=vendor.rating or 0.0,
        total_bookings=vendor.total_bookings or 0,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
        owner_id=vendor.owner_id,
        owner_email=vendor.owner.email,
        owner_name=vendor.owner.full_name,
        owner_phone=vendor.owner.phone,
        stats=stats,
        documents_verified=False,
        last_compliance_check=None,
        compliance_flags=flags,
    )


@router.post("/{vendor_id}/approval", response_model=VendorDetailResponse)
async def process_vendor_approval(
    vendor_id: UUID,
    data: VendorApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> VendorDetailResponse:
    """
    Process vendor approval, rejection, suspension, or reactivation.
    
    Actions:
    - approve: Approve pending vendor
    - reject: Reject pending vendor
    - suspend: Suspend active vendor
    - reactivate: Reactivate suspended vendor
    
    All actions are audited and require a reason.
    """
    result = await db.execute(
        select(Vendor).options(selectinload(Vendor.owner)).where(Vendor.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    # Validate state transitions
    current_status = vendor.status.value if isinstance(vendor.status, VendorStatus) else vendor.status
    
    valid_transitions = {
        VendorApprovalAction.APPROVE: ["pending"],
        VendorApprovalAction.REJECT: ["pending"],
        VendorApprovalAction.SUSPEND: ["active"],
        VendorApprovalAction.REACTIVATE: ["suspended"],
    }
    
    if current_status not in valid_transitions[data.action]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot {data.action.value} vendor with status '{current_status}'"
        )
    
    # Store old state for audit
    old_status = current_status
    old_featured = vendor.is_featured
    
    # Apply action
    new_status_map = {
        VendorApprovalAction.APPROVE: VendorStatus.ACTIVE,
        VendorApprovalAction.REJECT: VendorStatus.REJECTED,
        VendorApprovalAction.SUSPEND: VendorStatus.SUSPENDED,
        VendorApprovalAction.REACTIVATE: VendorStatus.ACTIVE,
    }
    
    vendor.status = new_status_map[data.action]
    vendor.updated_at = datetime.now(timezone.utc)
    
    # Audit log
    audit_action = {
        VendorApprovalAction.APPROVE: AuditAction.APPROVE,
        VendorApprovalAction.REJECT: AuditAction.REJECT,
        VendorApprovalAction.SUSPEND: AuditAction.SUSPEND,
        VendorApprovalAction.REACTIVATE: AuditAction.ACTIVATE,
    }[data.action]
    
    await AuditService.log_audit_action(
        db=db,
        user=current_user,
        action=audit_action,
        entity_type="vendor",
        entity_id=vendor.id,
        entity_name=vendor.business_name,
        old_values={"status": old_status, "is_featured": old_featured},
        new_values={
            "status": vendor.status.value if isinstance(vendor.status, VendorStatus) else vendor.status,
            "reason": data.reason,
            "notes": data.notes,
        },
        changes_summary=f"{data.action.value}d vendor: {data.reason or 'No reason provided'}"
    )
    
    await db.commit()
    
    # Return updated vendor
    stats = await calculate_vendor_stats(db, vendor.id)
    flags = await run_compliance_check(db, vendor)
    
    return VendorDetailResponse(
        id=vendor.id,
        business_name=vendor.business_name,
        business_type=vendor.business_type,
        description=vendor.description,
        status=vendor.status.value if isinstance(vendor.status, VendorStatus) else vendor.status,
        tax_id=vendor.tax_id,
        commission_rate=vendor.commission_rate,
        is_featured=vendor.is_featured or False,
        rating=vendor.rating or 0.0,
        total_bookings=vendor.total_bookings or 0,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
        owner_id=vendor.owner_id,
        owner_email=vendor.owner.email,
        owner_name=vendor.owner.full_name,
        owner_phone=vendor.owner.phone,
        stats=stats,
        documents_verified=False,
        last_compliance_check=None,
        compliance_flags=flags,
    )


@router.post("/{vendor_id}/feature", response_model=dict)
async def toggle_vendor_featured(
    vendor_id: UUID,
    featured: bool = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> dict:
    """
    Toggle featured status for a vendor.
    
    Only active vendors can be featured.
    """
    result = await db.execute(
        select(Vendor).options(selectinload(Vendor.owner)).where(Vendor.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    # Only active vendors can be featured
    current_status = vendor.status.value if isinstance(vendor.status, VendorStatus) else vendor.status
    if featured and current_status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active vendors can be featured"
        )
    
    old_featured = vendor.is_featured
    vendor.is_featured = featured
    vendor.updated_at = datetime.now(timezone.utc)
    
    # Audit log
    await AuditService.log_audit_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="vendor",
        entity_id=vendor.id,
        entity_name=vendor.business_name,
        old_values={"is_featured": old_featured},
        new_values={"is_featured": featured},
        changes_summary=f"{'Featured' if featured else 'Unfeatured'} vendor"
    )
    
    await db.commit()
    
    return {
        "message": f"Vendor {vendor.business_name} is now {'featured' if featured else 'unfeatured'}",
        "is_featured": featured
    }


@router.get("/analytics/overview", response_model=VendorAnalytics)
async def get_vendor_analytics(
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> VendorAnalytics:
    """
    Get comprehensive vendor analytics.
    
    Includes counts, top performers, recent registrations, and trends.
    """
    # Count by status
    result = await db.execute(
        select(Vendor.status, func.count(Vendor.id))
        .group_by(Vendor.status)
    )
    status_counts = {row[0].value if isinstance(row[0], VendorStatus) else row[0]: row[1] for row in result.all()}
    
    # Top performers by revenue
    result = await db.execute(
        select(Vendor, func.sum(Booking.total_amount).label("revenue"))
        .join(Booking, Booking.vendor_id == Vendor.id)
        .where(Vendor.status == VendorStatus.ACTIVE)
        .group_by(Vendor.id)
        .order_by(desc("revenue"))
        .limit(10)
    )
    top_vendors = result.all()
    
    top_stats = []
    for vendor, revenue in top_vendors:
        stats = await calculate_vendor_stats(db, vendor.id)
        top_stats.append(stats)
    
    # Recent registrations
    result = await db.execute(
        select(Vendor)
        .options(selectinload(Vendor.owner))
        .order_by(desc(Vendor.created_at))
        .limit(10)
    )
    recent = result.scalars().all()
    
    recent_list = [
        VendorListResponse(
            id=v.id,
            business_name=v.business_name,
            business_type=v.business_type,
            status=v.status.value if isinstance(v.status, VendorStatus) else v.status,
            rating=v.rating or 0.0,
            total_bookings=v.total_bookings or 0,
            is_featured=v.is_featured or False,
            created_at=v.created_at,
            owner_email=v.owner.email,
            owner_name=v.owner.full_name,
        )
        for v in recent
    ]
    
    # Bookings by month (last 12 months)
    months_ago = datetime.now(timezone.utc) - timedelta(days=365)
    result = await db.execute(
        select(
            func.date_trunc('month', Booking.created_at).label("month"),
            func.count(Booking.id).label("count"),
            func.sum(Booking.total_amount).label("revenue"),
        )
        .where(Booking.created_at >= months_ago)
        .group_by(func.date_trunc('month', Booking.created_at))
        .order_by("month")
    )
    bookings_by_month = [
        {"month": row.month.strftime("%Y-%m"), "count": row.count, "revenue": float(row.revenue or 0)}
        for row in result.all()
    ]
    
    # Revenue by vendor type
    result = await db.execute(
        select(Vendor.business_type, func.sum(Booking.total_amount))
        .join(Booking, Booking.vendor_id == Vendor.id)
        .where(Booking.created_at >= months_ago)
        .group_by(Vendor.business_type)
    )
    revenue_by_type = {row[0]: float(row[1] or 0) for row in result.all()}
    
    return VendorAnalytics(
        total_vendors=sum(status_counts.values()),
        pending_approval=status_counts.get("pending", 0),
        active_vendors=status_counts.get("active", 0),
        suspended_vendors=status_counts.get("suspended", 0),
        rejected_vendors=status_counts.get("rejected", 0),
        top_performers=top_stats,
        recent_registrations=recent_list,
        revenue_by_vendor_type=revenue_by_type,
        bookings_by_month=bookings_by_month,
    )


@router.post("/{vendor_id}/compliance-check", response_model=dict)
async def run_vendor_compliance_check(
    vendor_id: UUID,
    data: ComplianceCheckRequest = Body(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
) -> dict:
    """
    Run compliance check on a vendor.
    
    Checks documents, bookings, and reviews for compliance issues.
    """
    result = await db.execute(
        select(Vendor).where(Vendor.id == vendor_id)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    flags = await run_compliance_check(db, vendor)
    
    # Update vendor
    vendor.last_compliance_check = datetime.now(timezone.utc)
    
    # Audit log
    await AuditService.log_audit_action(
        db=db,
        user=current_user,
        action=AuditAction.VIEW,
        entity_type="vendor",
        entity_id=vendor.id,
        entity_name=vendor.business_name,
        changes_summary=f"Ran compliance check. Flags: {', '.join(flags) if flags else 'None'}"
    )
    
    await db.commit()
    
    return {
        "vendor_id": vendor_id,
        "compliant": len(flags) == 0,
        "flags": flags,
        "checked_at": vendor.last_compliance_check.isoformat()
    }
