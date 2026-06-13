"""
Vehicle Schemas - Rent a Car
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models import VehicleType, TransmissionType, FuelType


class VehicleBase(BaseModel):
    vehicle_type: VehicleType = VehicleType.CAR
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=2000, le=2030)
    transmission: TransmissionType = TransmissionType.AUTOMATIC
    fuel_type: FuelType = FuelType.GASOLINE
    seats: int = Field(default=5, ge=1, le=50)
    license_plate: Optional[str] = None
    color: Optional[str] = None
    mileage: int = 0
    features: dict = {}
    images: List[str] = []
    price_per_day: float = 0
    price_per_week: float = 0
    price_per_month: float = 0
    insurance_options: dict = {}
    deposit_amount: float = 0
    location: Optional[str] = None
    pickup_locations: List[str] = []
    dropoff_locations: List[str] = []
    requirements: List[str] = []


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_type: Optional[VehicleType] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    transmission: Optional[TransmissionType] = None
    fuel_type: Optional[FuelType] = None
    seats: Optional[int] = None
    license_plate: Optional[str] = None
    color: Optional[str] = None
    mileage: Optional[int] = None
    features: Optional[dict] = None
    images: Optional[List[str]] = None
    price_per_day: Optional[float] = None
    price_per_week: Optional[float] = None
    price_per_month: Optional[float] = None
    insurance_options: Optional[dict] = None
    deposit_amount: Optional[float] = None
    location: Optional[str] = None
    pickup_locations: Optional[List[str]] = None
    dropoff_locations: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    is_available: Optional[bool] = None


class VehicleResponse(VehicleBase):
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


class VehicleDetailResponse(VehicleResponse):
    pass
