import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, desc

from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_permission
from app.models import User, UserRole, TripPlan, TripItem
from app.schemas import PaginationParams, PaginatedResponse
from app.core.pagination import paginate_flat
from app.services.trip_pricing import (
    fetch_item_price,
    compute_package_discounts,
    compute_summary,
)

router = APIRouter(tags=["Trip Planner"])

# ============================================================================
# Schemas
# ============================================================================


class TripItemCreate(BaseModel):
    day_index: int = Field(..., ge=0)
    item_type: str = Field(
        ...,
        pattern=r"^(accommodation|tour|transport|car_rental|boat|flight|meal|other)$",
    )
    reference_type: str = Field(
        ..., pattern=r"^(property|tour|transportation|flight|vehicle|boat)$"
    )
    reference_id: uuid.UUID
    label: Optional[str] = None
    location: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    notes: Optional[str] = None


class TripItemUpdate(BaseModel):
    day_index: Optional[int] = None
    label: Optional[str] = None
    location: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=1)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    sort_order: Optional[int] = None
    notes: Optional[str] = None


class TripPlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    travelers: int = Field(default=1, ge=1, le=100)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    notes: Optional[str] = None


class TripPlanUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    status: Optional[str] = Field(
        default=None, pattern=r"^(draft|pricing|ready|booked)$"
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    travelers: Optional[int] = Field(default=None, ge=1, le=100)
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    notes: Optional[str] = None
    is_shared: Optional[bool] = None


class TripItemResponse(BaseModel):
    id: str
    day_index: int
    item_type: str
    reference_type: str
    reference_id: str
    label: Optional[str]
    location: Optional[str]
    quantity: int
    unit_price: float
    total_price: float
    commission_amount: float
    vendor_payout: float
    currency: str
    status: str
    sort_order: int
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TripPlanResponse(BaseModel):
    id: str
    user_id: str
    name: str
    status: str
    start_date: Optional[str]
    end_date: Optional[str]
    travelers: int
    budget_min: Optional[float]
    budget_max: Optional[float]
    notes: Optional[str]
    total_estimated: float
    currency: str
    is_shared: bool
    is_template: bool
    items: list[TripItemResponse] = []
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class PriceBreakdownItem(BaseModel):
    label: Optional[str]
    item_type: str
    unit_price: float
    total_price: float
    commission_amount: float
    vendor_payout: float
    breakdown: dict = {}


class DiscountInfo(BaseModel):
    rule: str
    label: str
    discount_percent: float
    discount_amount: float
    applied_to: list[str] = []


class PriceSummary(BaseModel):
    subtotal: float
    discounts: list[DiscountInfo] = []
    total_discount: float
    after_discounts: float
    total_commission: float
    total_vendor_payout: float
    platform_revenue: float
    grand_total: float
    items_count: int
    currency: str


class TripPlanPriceResponse(BaseModel):
    plan_id: str
    items: list[PriceBreakdownItem]
    summary: PriceSummary


def _serialize_item(item: TripItem) -> dict:
    return {
        "id": str(item.id),
        "day_index": item.day_index,
        "item_type": item.item_type,
        "reference_type": item.reference_type,
        "reference_id": str(item.reference_id),
        "label": item.label,
        "location": item.location,
        "quantity": item.quantity,
        "unit_price": item.unit_price,
        "total_price": item.total_price,
        "commission_amount": item.commission_amount,
        "vendor_payout": item.vendor_payout,
        "currency": item.currency,
        "status": item.status,
        "sort_order": item.sort_order,
        "notes": item.notes,
        "created_at": item.created_at.isoformat() if item.created_at else "",
        "updated_at": item.updated_at.isoformat() if item.updated_at else "",
    }


# ============================================================================
# Plan CRUD
# ============================================================================


@router.post("/plans", response_model=TripPlanResponse, status_code=201)
@limiter.limit("10/minute")
async def create_plan(
    request: Request,
    data: TripPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "create")),
):
    plan = TripPlan(
        user_id=current_user.id,
        name=data.name,
        status="draft",
        travelers=data.travelers,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
        notes=data.notes,
    )
    if data.start_date:
        plan.start_date = datetime.fromisoformat(data.start_date)
    if data.end_date:
        plan.end_date = datetime.fromisoformat(data.end_date)

    db.add(plan)
    await db.flush()
    await db.commit()
    await db.refresh(plan)

    return {
        "id": str(plan.id),
        "user_id": str(plan.user_id),
        "name": plan.name,
        "status": plan.status,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
        "travelers": plan.travelers,
        "budget_min": plan.budget_min,
        "budget_max": plan.budget_max,
        "notes": plan.notes,
        "total_estimated": plan.total_estimated,
        "currency": plan.currency,
        "is_shared": plan.is_shared,
        "is_template": plan.is_template,
        "items": [],
        "created_at": plan.created_at.isoformat() if plan.created_at else "",
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else "",
    }


@router.get("/plans", response_model=PaginatedResponse)
async def list_plans(
    params: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "read")),
):
    query = select(TripPlan).where(TripPlan.user_id == current_user.id)
    if status_filter:
        query = query.where(TripPlan.status == status_filter)
    query = query.order_by(desc(TripPlan.updated_at))

    response = await paginate_flat(
        db,
        query,
        params,
        transform_func=lambda p: {
            "id": str(p.id),
            "name": p.name,
            "status": p.status,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "travelers": p.travelers,
            "total_estimated": p.total_estimated,
            "currency": p.currency,
            "created_at": p.created_at.isoformat() if p.created_at else "",
            "updated_at": p.updated_at.isoformat() if p.updated_at else "",
        },
        order_by=TripPlan.updated_at.desc(),
    )
    return response


@router.get("/plans/{plan_id}", response_model=TripPlanResponse)
async def get_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "read")),
):
    result = await db.execute(select(TripPlan).where(TripPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    items_result = await db.execute(
        select(TripItem)
        .where(TripItem.plan_id == plan_id)
        .order_by(TripItem.day_index, TripItem.sort_order)
    )
    items = items_result.scalars().all()

    return {
        "id": str(plan.id),
        "user_id": str(plan.user_id),
        "name": plan.name,
        "status": plan.status,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
        "travelers": plan.travelers,
        "budget_min": plan.budget_min,
        "budget_max": plan.budget_max,
        "notes": plan.notes,
        "total_estimated": plan.total_estimated,
        "currency": plan.currency,
        "is_shared": plan.is_shared,
        "is_template": plan.is_template,
        "items": [_serialize_item(i) for i in items],
        "created_at": plan.created_at.isoformat() if plan.created_at else "",
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else "",
    }


@router.put("/plans/{plan_id}", response_model=TripPlanResponse)
@limiter.limit("10/minute")
async def update_plan(
    request: Request,
    plan_id: uuid.UUID,
    data: TripPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "update")),
):
    result = await db.execute(select(TripPlan).where(TripPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    if data.name is not None:
        plan.name = data.name
    if data.status is not None:
        plan.status = data.status
    if data.start_date is not None:
        plan.start_date = datetime.fromisoformat(data.start_date)
    if data.end_date is not None:
        plan.end_date = datetime.fromisoformat(data.end_date)
    if data.travelers is not None:
        plan.travelers = data.travelers
    if data.budget_min is not None:
        plan.budget_min = data.budget_min
    if data.budget_max is not None:
        plan.budget_max = data.budget_max
    if data.notes is not None:
        plan.notes = data.notes
    if data.is_shared is not None:
        plan.is_shared = data.is_shared

    await db.commit()
    await db.refresh(plan)

    items_result = await db.execute(
        select(TripItem)
        .where(TripItem.plan_id == plan_id)
        .order_by(TripItem.day_index, TripItem.sort_order)
    )
    items = items_result.scalars().all()

    return {
        "id": str(plan.id),
        "user_id": str(plan.user_id),
        "name": plan.name,
        "status": plan.status,
        "start_date": plan.start_date.isoformat() if plan.start_date else None,
        "end_date": plan.end_date.isoformat() if plan.end_date else None,
        "travelers": plan.travelers,
        "budget_min": plan.budget_min,
        "budget_max": plan.budget_max,
        "notes": plan.notes,
        "total_estimated": plan.total_estimated,
        "currency": plan.currency,
        "is_shared": plan.is_shared,
        "is_template": plan.is_template,
        "items": [_serialize_item(i) for i in items],
        "created_at": plan.created_at.isoformat() if plan.created_at else "",
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else "",
    }


@router.delete("/plans/{plan_id}", response_model=dict)
async def delete_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "update")),
):
    result = await db.execute(select(TripPlan).where(TripPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(plan)
    await db.commit()
    return {"message": "Plan deleted"}


# ============================================================================
# Items
# ============================================================================


@router.post("/plans/{plan_id}/items", response_model=TripItemResponse, status_code=201)
@limiter.limit("10/minute")
async def add_item(
    request: Request,
    plan_id: uuid.UUID,
    data: TripItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "create")),
):
    result = await db.execute(select(TripPlan).where(TripPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    item = TripItem(
        plan_id=plan_id,
        day_index=data.day_index,
        item_type=data.item_type,
        reference_type=data.reference_type,
        reference_id=data.reference_id,
        label=data.label,
        location=data.location,
        quantity=data.quantity,
    )
    if data.start_time:
        item.start_time = datetime.fromisoformat(data.start_time).time()
    if data.end_time:
        item.end_time = datetime.fromisoformat(data.end_time).time()
    if data.notes:
        item.notes = data.notes

    try:
        pricing = await fetch_item_price(
            db=db,
            item_type=data.item_type,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            quantity=data.quantity,
            travelers=plan.travelers,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    item.unit_price = pricing["unit_price"]
    item.total_price = pricing["total_price"]
    item.commission_rate = pricing["commission_rate"]
    item.commission_amount = pricing["commission_amount"]
    item.vendor_payout = pricing["vendor_payout"]

    db.add(item)
    await db.flush()

    await _recompute_plan_total(db, plan)

    await db.commit()
    await db.refresh(item)

    return _serialize_item(item)


@router.put("/items/{item_id}", response_model=TripItemResponse)
@limiter.limit("10/minute")
async def update_item(
    request: Request,
    item_id: uuid.UUID,
    data: TripItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "update")),
):
    result = await db.execute(select(TripItem).where(TripItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    plan_result = await db.execute(select(TripPlan).where(TripPlan.id == item.plan_id))
    plan = plan_result.scalar_one_or_none()
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    if data.day_index is not None:
        item.day_index = data.day_index
    if data.label is not None:
        item.label = data.label
    if data.location is not None:
        item.location = data.location
    if data.quantity is not None:
        old_qty = item.quantity
        item.quantity = data.quantity
        item.unit_price = (
            round(item.unit_price * data.quantity / old_qty, 2) if old_qty else 0
        )
        item.total_price = item.unit_price * item.quantity if old_qty else 0
    if data.start_time is not None:
        item.start_time = datetime.fromisoformat(data.start_time).time()
    if data.end_time is not None:
        item.end_time = datetime.fromisoformat(data.end_time).time()
    if data.sort_order is not None:
        item.sort_order = data.sort_order
    if data.notes is not None:
        item.notes = data.notes

    await _recompute_plan_total(db, plan)

    await db.commit()
    await db.refresh(item)

    return _serialize_item(item)


@router.delete("/items/{item_id}", response_model=dict)
async def delete_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "update")),
):
    result = await db.execute(select(TripItem).where(TripItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    plan_result = await db.execute(select(TripPlan).where(TripPlan.id == item.plan_id))
    plan = plan_result.scalar_one_or_none()
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(item)
    await _recompute_plan_total(db, plan)
    await db.commit()

    return {"message": "Item removed from plan"}


# ============================================================================
# Pricing
# ============================================================================


@router.get("/plans/{plan_id}/price", response_model=TripPlanPriceResponse)
async def get_plan_price(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "read")),
):
    result = await db.execute(select(TripPlan).where(TripPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    items_result = await db.execute(
        select(TripItem)
        .where(TripItem.plan_id == plan_id)
        .order_by(TripItem.day_index, TripItem.sort_order)
    )
    items = items_result.scalars().all()

    item_data = []
    for item in items:
        try:
            pricing = await fetch_item_price(
                db=db,
                item_type=item.item_type,
                reference_type=item.reference_type,
                reference_id=item.reference_id,
                quantity=item.quantity,
                travelers=plan.travelers,
            )
        except ValueError:
            pricing = {
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "commission_amount": item.commission_amount,
                "vendor_payout": item.vendor_payout,
                "breakdown": {},
            }

        item_data.append(
            {
                "label": item.label,
                "item_type": item.item_type,
                "unit_price": pricing["unit_price"],
                "total_price": pricing["total_price"],
                "commission_amount": pricing["commission_amount"],
                "vendor_payout": pricing["vendor_payout"],
                "breakdown": pricing.get("breakdown", {}),
            }
        )

    discounts = compute_package_discounts(item_data)
    summary = compute_summary(item_data, discounts)

    return TripPlanPriceResponse(
        plan_id=str(plan_id),
        items=[PriceBreakdownItem(**i) for i in item_data],
        summary=PriceSummary(**summary),
    )


@router.post("/plans/{plan_id}/reprice", response_model=TripPlanResponse)
@limiter.limit("10/minute")
async def reprice_plan(
    request: Request,
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("bookings", "update")),
):
    result = await db.execute(select(TripPlan).where(TripPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    items_result = await db.execute(select(TripItem).where(TripItem.plan_id == plan_id))
    items = items_result.scalars().all()

    for item in items:
        try:
            pricing = await fetch_item_price(
                db=db,
                item_type=item.item_type,
                reference_type=item.reference_type,
                reference_id=item.reference_id,
                quantity=item.quantity,
                travelers=plan.travelers,
            )
            item.unit_price = pricing["unit_price"]
            item.total_price = pricing["total_price"]
            item.commission_rate = pricing["commission_rate"]
            item.commission_amount = pricing["commission_amount"]
            item.vendor_payout = pricing["vendor_payout"]
        except ValueError:
            pass

    await _recompute_plan_total(db, plan)
    await db.commit()

    return await get_plan(plan_id, db, current_user)


async def _recompute_plan_total(db: AsyncSession, plan: TripPlan):
    items_result = await db.execute(select(TripItem).where(TripItem.plan_id == plan.id))
    items = items_result.scalars().all()
    plan.total_estimated = round(sum(i.total_price for i in items), 2)
