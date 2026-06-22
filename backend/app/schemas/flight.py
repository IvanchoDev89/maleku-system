"""
Flight Schemas - Vuelos
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models import RouteType
from . import is_dangerous_sql


def _sanitize_flight_field(cls, v: Optional[str]) -> Optional[str]:
    if v is not None and is_dangerous_sql(v):
        raise ValueError("Invalid input")
    return v


class FlightBase(BaseModel):
    airline: str = Field(..., min_length=1, max_length=100)
    flight_number: str = Field(..., min_length=1, max_length=20)
    route_type: RouteType = RouteType.DOMESTIC
    origin_airport: str = Field(..., min_length=2, max_length=10)
    destination_airport: str = Field(..., min_length=2, max_length=10)
    departure_time: str = Field(..., min_length=4, max_length=10)
    arrival_time: str = Field(..., min_length=4, max_length=10)
    duration_minutes: int = Field(..., ge=1)
    aircraft_type: Optional[str] = None
    price_economy: float = 0
    price_business: float = 0
    price_first: float = 0
    currency: str = "USD"
    baggage_allowance: dict = {}
    amenities: List[str] = []
    schedule_days: List[str] = []

    @field_validator(
        "airline",
        "flight_number",
        "origin_airport",
        "destination_airport",
        "aircraft_type",
    )
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        return _sanitize_flight_field(cls, v)


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    route_type: Optional[RouteType] = None
    origin_airport: Optional[str] = None
    destination_airport: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    aircraft_type: Optional[str] = None
    price_economy: Optional[float] = None
    price_business: Optional[float] = None
    price_first: Optional[float] = None
    currency: Optional[str] = None
    baggage_allowance: Optional[dict] = None
    amenities: Optional[List[str]] = None
    schedule_days: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @field_validator(
        "airline",
        "flight_number",
        "origin_airport",
        "destination_airport",
        "aircraft_type",
    )
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        return _sanitize_flight_field(cls, v)


class FlightResponse(FlightBase):
    id: UUID
    vendor_id: Optional[UUID]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FlightDetailResponse(FlightResponse):
    pass
