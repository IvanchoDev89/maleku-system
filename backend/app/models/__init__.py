"""
Models package for Costa Rica Travel application.
All models are organized into separate modules by domain.
"""

# Import Base first (re-export from database module)
from app.core.database import Base
from app.models.audit import (
    AuditAction,
    AuditLog,
    PointOfSale,
    RolePermission,
    SecurityAction,
    SecurityLog,
)

# Import all models for re-export
from app.models.base import (
    BlogPostStatus,
    BookingStatus,
    UserRole,
    VendorStatus,
)
from app.models.blog import BlogPost
from app.models.boat import Boat as BoatEquipment
from app.models.boat import BoatType
from app.models.booking import Booking, ProcessedWebhook
from app.models.chat import ChatServiceType, Conversation, Message, MessageType
from app.models.destination import Destination
from app.models.property import Property, PropertyType, Room
from app.models.review import Review
from app.models.room_availability import RoomAvailability
from app.models.tour import Tour, TourCategory, TourDifficulty
from app.models.user import User
from app.models.vehicle import FuelType, TransmissionType, Vehicle, VehicleType
from app.models.vendor import Vendor

# Alias for backward compatibility
Boat = BoatEquipment
from app.models.content import MediaFile, SEOSettings, StaticPage
from app.models.flight import Flight, RouteType
from app.models.marketing import (
    CampaignStatus,
    CampaignType,
    EmailCampaign,
    EmailLog,
    EmailPreference,
    EmailTemplate,
    InboxMessage,
    MarketingAutomation,
    RecipientType,
)
from app.models.newsletter import NewsletterSubscriber
from app.models.planner import PlannerLead
from app.models.pricing import PricingRule

# Additional enums from property
from app.models.property import PropertyCategory
from app.models.transportation import (
    DayType,
    PricingType,
    Transportation,
    TransportServiceType,
    TransportVehicleType,
)
from app.models.trip_planner import TripItem, TripPlan

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
    "Boat",
    "BoatEquipment",
    # Content Models
    "StaticPage",
    "SEOSettings",
    "MediaFile",
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
