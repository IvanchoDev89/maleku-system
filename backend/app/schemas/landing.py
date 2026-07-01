from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LandingPropertyItem(BaseModel):
    id: UUID
    name: str
    slug: str
    cover_image: str | None = None
    property_type: str = "hotel"
    city: str | None = None
    region: str | None = None
    base_price: float = 0
    rating: float | None = 0.0
    total_reviews: int = 0

    model_config = ConfigDict(from_attributes=True)


class LandingTourItem(BaseModel):
    id: UUID
    name: str
    slug: str
    cover_image: str | None = None
    category: str
    duration_hours: float = 0
    location: str | None = None
    price: float = 0
    rating: float | None = 0.0
    total_reviews: int = 0

    model_config = ConfigDict(from_attributes=True)


class LandingVehicleItem(BaseModel):
    id: UUID
    brand: str
    model: str
    vehicle_type: str = "car"
    seats: int = 5
    images: list[str] = []
    price_per_day: float = 0
    rating: float = 0.0
    total_reviews: int = 0

    model_config = ConfigDict(from_attributes=True)


class LandingBoatItem(BaseModel):
    id: UUID
    brand: str | None = None
    model: str | None = None
    equipment_type: str = "boat"
    capacity: int = 4
    images: list[str] = []
    price_per_day: float = 0
    rating: float = 0.0
    total_reviews: int = 0

    model_config = ConfigDict(from_attributes=True)


class LandingTransportItem(BaseModel):
    id: UUID
    service_type: str = "airport_transfer"
    vehicle_type: str = "sedan"
    vehicle_description: str | None = None
    capacity: int = 4
    images: list[str] = []
    base_price: float = 0
    rating: float = 0.0
    total_reviews: int = 0

    model_config = ConfigDict(from_attributes=True)


class LandingReview(BaseModel):
    id: UUID
    rating: int
    title: str | None = None
    comment: str | None = None
    user_name: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LandingStats(BaseModel):
    total_properties: int = 0
    total_tours: int = 0
    total_vehicles: int = 0
    total_boats: int = 0
    total_transportation: int = 0
    total_reviews: int = 0
    total_bookings: int = 0
    member_since: datetime | None = None


class LandingRanking(BaseModel):
    position: int = 0
    total_vendors: int = 0


class VendorLandingResponse(BaseModel):
    id: UUID
    business_name: str
    business_slug: str
    business_type: str
    description: str | None = None
    logo_url: str | None = None
    cover_image: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    rating: float | None = 0.0
    total_reviews: int = 0
    is_verified: bool = False

    properties: list[LandingPropertyItem] = []
    properties_has_more: bool = False
    tours: list[LandingTourItem] = []
    tours_has_more: bool = False
    vehicles: list[LandingVehicleItem] = []
    vehicles_has_more: bool = False
    boats: list[LandingBoatItem] = []
    boats_has_more: bool = False
    transportation: list[LandingTransportItem] = []
    transportation_has_more: bool = False

    reviews: list[LandingReview] = []
    reviews_total: int = 0
    reviews_average_rating: float = 0.0

    stats: LandingStats
    ranking: LandingRanking
    can_review: bool = False
    eligible_booking_ids: list[str] = []

    model_config = ConfigDict(from_attributes=True)
