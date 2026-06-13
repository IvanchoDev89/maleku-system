"""
Pricing Rule Schemas - Precios Dinámicos
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models import DayType


class PricingRuleBase(BaseModel):
    service_type: str = Field(..., min_length=1, max_length=50)
    base_price: float = Field(..., ge=0)
    demand_multiplier: float = Field(default=1.0, ge=0.8, le=3.0)
    seasonal_multiplier: float = Field(default=1.0, ge=0.8, le=1.5)
    date_from: datetime
    date_to: Optional[datetime] = None
    day_type: Optional[DayType] = None
    min_occupancy: Optional[int] = Field(None, ge=1)
    max_occupancy: Optional[int] = Field(None, ge=1)
    advance_booking_days: Optional[int] = Field(None, ge=1)
    advance_discount_percent: float = Field(default=0, ge=0, le=100)


class PricingRuleCreate(PricingRuleBase):
    service_id: UUID


class PricingRuleUpdate(BaseModel):
    base_price: Optional[float] = None
    demand_multiplier: Optional[float] = None
    seasonal_multiplier: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    day_type: Optional[DayType] = None
    min_occupancy: Optional[int] = None
    max_occupancy: Optional[int] = None
    advance_booking_days: Optional[int] = None
    advance_discount_percent: Optional[float] = None
    is_active: Optional[bool] = None


class PricingRuleResponse(PricingRuleBase):
    id: UUID
    service_id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PricingRuleDetailResponse(PricingRuleResponse):
    final_price: float

    model_config = ConfigDict(from_attributes=True)
