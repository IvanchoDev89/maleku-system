"""
Boat Equipment Schemas - Náutico
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models import BoatType


class BoatEquipmentBase(BaseModel):
    equipment_type: BoatType = BoatType.BOAT
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=2000, le=2030)
    capacity: int = Field(default=4, ge=1, le=100)
    length_foot: Optional[float] = None
    features: dict = {}
    images: List[str] = []
    price_per_hour: float = 0
    price_per_day: float = 0
    price_per_week: float = 0
    requires_license: bool = False
    license_notes: Optional[str] = None
    location: Optional[str] = None
    operating_area: Optional[str] = None


class BoatEquipmentCreate(BoatEquipmentBase):
    pass


class BoatEquipmentUpdate(BaseModel):
    equipment_type: Optional[BoatType] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity: Optional[int] = None
    length_foot: Optional[float] = None
    features: Optional[dict] = None
    images: Optional[List[str]] = None
    price_per_hour: Optional[float] = None
    price_per_day: Optional[float] = None
    price_per_week: Optional[float] = None
    requires_license: Optional[bool] = None
    license_notes: Optional[str] = None
    location: Optional[str] = None
    operating_area: Optional[str] = None
    is_available: Optional[bool] = None


class BoatEquipmentResponse(BoatEquipmentBase):
    id: UUID
    vendor_id: UUID
    rating: float = 0.0
    total_reviews: int = 0
    total_rentals: int = 0
    is_available: bool = True
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BoatEquipmentDetailResponse(BoatEquipmentResponse):
    pass