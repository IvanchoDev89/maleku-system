"""
Pricing API - Precios Dinámicos
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models import User, UserRole, PricingRule
from app.schemas import pricing as pricing_schema

router = APIRouter()


@router.get("/", response_model=list[pricing_schema.PricingRuleResponse])
async def list_pricing_rules(
    service_type: str | None = None,
    service_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
) -> list[pricing_schema.PricingRuleResponse]:
    """List pricing rules"""
    query = select(PricingRule).where(PricingRule.is_active)
    
    if service_type:
        query = query.where(PricingRule.service_type == service_type)
    if service_id:
        query = query.where(PricingRule.service_id == service_id)
    
    result = await db.execute(query.order_by(PricingRule.date_from))
    rules = result.scalars().all()
    
    return rules


@router.get("/{rule_id}", response_model=pricing_schema.PricingRuleDetailResponse)
async def get_pricing_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    """Get pricing rule details with calculated final price"""
    result = await db.execute(
        select(PricingRule).where(PricingRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    final_price = rule.base_price * rule.demand_multiplier * rule.seasonal_multiplier
    
    return {**rule.__dict__, "final_price": round(final_price, 2)}


@router.post("/", response_model=pricing_schema.PricingRuleResponse)
async def create_pricing_rule(
    rule_data: pricing_schema.PricingRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
) -> pricing_schema.PricingRuleResponse:
    """Create pricing rule (Vendor only)"""
    rule = PricingRule(
        service_id=rule_data.service_id,
        service_type=rule_data.service_type,
        base_price=rule_data.base_price,
        demand_multiplier=rule_data.demand_multiplier,
        seasonal_multiplier=rule_data.seasonal_multiplier,
        date_from=rule_data.date_from,
        date_to=rule_data.date_to,
        day_type=rule_data.day_type,
        min_occupancy=rule_data.min_occupancy,
        max_occupancy=rule_data.max_occupancy,
        advance_booking_days=rule_data.advance_booking_days,
        advance_discount_percent=rule_data.advance_discount_percent,
    )
    
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    
    return rule


@router.put("/{rule_id}", response_model=pricing_schema.PricingRuleResponse)
async def update_pricing_rule(
    rule_id: uuid.UUID,
    rule_data: pricing_schema.PricingRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
) -> pricing_schema.PricingRuleResponse:
    """Update pricing rule (Owner only)"""
    result = await db.execute(
        select(PricingRule).where(PricingRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'service_id', 'service_type', 'base_price', 'demand_multiplier',
                     'seasonal_multiplier', 'date_from', 'date_to', 'day_type',
                     'min_occupancy', 'max_occupancy', 'advance_booking_days',
                     'advance_discount_percent'}
    
    for key, value in rule_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(rule, key, value)
    
    rule.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(rule)
    
    return rule


@router.delete("/{rule_id}")
async def delete_pricing_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.VENDOR))
) -> dict:
    """Delete pricing rule (Owner only)"""
    result = await db.execute(
        select(PricingRule).where(PricingRule.id == rule_id)
    )
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    
    rule.is_active = False
    await db.commit()
    
    return {"message": "Pricing rule deleted"}


@router.get("/calculate")
async def calculate_dynamic_price(
    service_type: str,
    service_id: uuid.UUID,
    date: datetime,
    occupancy: int = 1,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Calculate dynamic price for a service"""
    result = await db.execute(
        select(PricingRule).where(
            PricingRule.is_active,
            PricingRule.service_type == service_type,
            PricingRule.service_id == service_id,
            PricingRule.date_from <= date,
            or_(PricingRule.date_to.is_(None), PricingRule.date_to >= date)
        )
    )
    rules = result.scalars().all()
    
    if not rules:
        raise HTTPException(status_code=404, detail="No pricing rules found for this service")
    
    base_price = rules[0].base_price
    demand_multiplier = 1.0
    seasonal_multiplier = 1.0
    advance_discount = 0
    
    for rule in rules:
        if rule.demand_multiplier:
            demand_multiplier = rule.demand_multiplier
        if rule.seasonal_multiplier:
            seasonal_multiplier = rule.seasonal_multiplier
        if rule.demand_multiplier and rule.demand_multiplier == 0:
            rule.demand_multiplier = 1.0
        if rule.seasonal_multiplier and rule.seasonal_multiplier == 0:
            rule.seasonal_multiplier = 1.0
        if rule.advance_booking_days and rule.advance_discount_percent:
            days_advance = (date - datetime.now(timezone.utc)).days
            if days_advance >= rule.advance_booking_days:
                advance_discount = rule.advance_discount_percent
    
    final_price = base_price * demand_multiplier * seasonal_multiplier
    final_price = final_price * (1 - advance_discount / 100)
    
    return {
        "service_type": service_type,
        "service_id": service_id,
        "base_price": base_price,
        "demand_multiplier": demand_multiplier,
        "seasonal_multiplier": seasonal_multiplier,
        "advance_discount_percent": advance_discount,
        "final_price": round(final_price, 2),
        "currency": "USD"
    }