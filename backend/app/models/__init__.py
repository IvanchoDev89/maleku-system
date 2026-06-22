"""
Models package for Costa Rica Travel application.
All models are organized into separate modules by domain.
"""

# Import Base first (re-export from database module)
from app.core.database import Base

# Import all models for re-export
from app.models.base import (
    UserRole,
    VendorStatus,
    BookingStatus,
    BlogPostStatus,
    TourType,
)

from app.models.property import PropertyType

from app.models.audit import (
    AuditAction,
    SecurityAction,
    AuditLog,
    SecurityLog,
    RolePermission,
    PointOfSale,
)

from app.models.user import User
from app.models.vendor import Vendor
from app.models.property import Property, Room
from app.models.room_availability import RoomAvailability
from app.models.tour import Tour, TourCategory, TourDifficulty
from app.models.booking import Booking, ProcessedWebhook
from app.models.blog import BlogPost
from app.models.review import Review
from app.models.destination import Destination
from app.models.chat import Conversation, Message, ChatServiceType, MessageType
from app.models.vehicle import Vehicle, VehicleType, TransmissionType, FuelType
from app.models.boat import Boat as BoatEquipment, BoatType
from app.models.flight import Flight, RouteType
from app.models.transportation import (
    Transportation,
    TransportServiceType,
    TransportVehicleType,
    PricingType,
    DayType,
)
from app.models.pricing import PricingRule
from app.models.newsletter import NewsletterSubscriber
from app.models.planner import PlannerLead
from app.models.trip_planner import TripPlan, TripItem

from app.models.marketing import (
    CampaignStatus,
    CampaignType,
    RecipientType,
    EmailCampaign,
    EmailTemplate,
    EmailLog,
    MarketingAutomation,
    InboxMessage,
    EmailPreference,
)

# Additional enums from property
from app.models.property import PropertyCategory

__all__ = [
    # Base
    "Base",
    # Enums
    "UserRole",
    "VendorStatus",
    "BookingStatus",
    "BlogPostStatus",
    "PropertyType",
    "PropertyCategory",
    "TourType",
    "TourCategory",
    "TourDifficulty",
    "ChatServiceType",
    "MessageType",
    "VehicleType",
    "TransmissionType",
    "FuelType",
    "BoatType",
    "RouteType",
    "TransportServiceType",
    "TransportVehicleType",
    "PricingType",
    "DayType",
    # Audit Enums
    "AuditAction",
    "SecurityAction",
    # Models
    "User",
    "Vendor",
    "Property",
    "Room",
    "RoomAvailability",
    "Tour",
    "Booking",
    "ProcessedWebhook",
    "BlogPost",
    "Review",
    "Destination",
    "Conversation",
    "Message",
    "Vehicle",
    "BoatEquipment",
    "Flight",
    "Transportation",
    "PricingRule",
    "NewsletterSubscriber",
    "PlannerLead",
    # Trip Planner Models
    "TripPlan",
    "TripItem",
    # Marketing Models
    "CampaignStatus",
    "CampaignType",
    "RecipientType",
    "EmailCampaign",
    "EmailTemplate",
    "EmailLog",
    "MarketingAutomation",
    "InboxMessage",
    "EmailPreference",
    # Audit Models
    "AuditLog",
    "SecurityLog",
    "RolePermission",
    "PointOfSale",
]
