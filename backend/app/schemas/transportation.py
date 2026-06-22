"""
Transportation Schemas - Transporte Privado
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models import TransportServiceType, TransportVehicleType, PricingType
from . import is_dangerous_sql


def _sanitize_transport_field(cls, v: Optional[str]) -> Optional[str]:
    if v is not None and is_dangerous_sql(v):
        raise ValueError("Invalid input")
    return v


class TransportationBase(BaseModel):
    service_type: TransportServiceType = TransportServiceType.AIRPORT_TRANSFER
    vehicle_type: TransportVehicleType = TransportVehicleType.SEDAN
    vehicle_description: Optional[str] = None
    capacity: int = Field(default=4, ge=1, le=50)
    features: dict = {}
    images: List[str] = []
    pricing_type: PricingType = PricingType.PER_ROUTE
    base_price: float = 0
    price_per_km: float = 0
    price_per_hour: float = 0
    routes_served: List[dict] = []
    locations: List[str] = []

    @field_validator("vehicle_description")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        return _sanitize_transport_field(cls, v)


class TransportationCreate(TransportationBase):
    pass


class TransportationUpdate(BaseModel):
    service_type: Optional[TransportServiceType] = None
    vehicle_type: Optional[TransportVehicleType] = None
    vehicle_description: Optional[str] = None
    capacity: Optional[int] = None
    features: Optional[dict] = None
    images: Optional[List[str]] = None
    pricing_type: Optional[PricingType] = None
    base_price: Optional[float] = None
    price_per_km: Optional[float] = None
    price_per_hour: Optional[float] = None
    routes_served: Optional[List[dict]] = None
    locations: Optional[List[str]] = None
    is_available: Optional[bool] = None

    @field_validator("vehicle_description")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        return _sanitize_transport_field(cls, v)


class TransportationResponse(TransportationBase):
    id: UUID
    vendor_id: UUID
    rating: float = 0.0
    total_reviews: int = 0
    total_bookings: int = 0
    is_available: bool = True
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransportationDetailResponse(TransportationResponse):
    pass
