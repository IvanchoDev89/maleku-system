import re
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def sanitize_html(value: str) -> str:
    """Remove HTML tags"""
    return re.sub(r"<[^>]+>", "", value)


def is_dangerous_sql(value: str) -> bool:
    """Check for SQL injection patterns"""
    dangerous = [
        "DROP",
        "DELETE",
        "INSERT",
        "UPDATE",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "--",
        "/*",
        "*/",
        "xp_",
        "sp_",
        "@@",
        " char ",
        " nchar ",
    ]
    upper = value.upper()
    return any(d in upper for d in dangerous)


COMMON_PASSWORDS = {
    "password",
    "12345678",
    "123456789",
    "qwerty123",
    "abc123",
    "letmein",
    "welcome",
    "monkey",
    "dragon",
    "master",
    "password1",
    "Password1",
    "Password123",
    "admin123",
    "costa rica",
    "costarica",
    "travel",
    "CostaRica",
}


def is_weak_password(value: str) -> bool:
    """Check password strength"""
    value = value.strip()
    if len(value) < 8:
        return True
    if not re.search(r"[A-Z]", value):
        return True
    if not re.search(r"[a-z]", value):
        return True
    if not re.search(r"[0-9]", value):
        return True
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        return True
    if value.lower() in COMMON_PASSWORDS:
        return True
    return False


# ============== USER SCHEMAS ==============
class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, min_length=8, max_length=20)

    @field_validator("full_name", "phone")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid characters in input")
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()
        if is_weak_password(v):
            raise ValueError(
                "Password must be 8+ chars with uppercase, lowercase, number, and special character"
            )
        return v


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    full_name: str | None = Field(None, min_length=2, max_length=255)
    phone: str | None = Field(None, min_length=8, max_length=20)
    avatar_url: str | None = None

    @field_validator("full_name", "phone")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid characters in input")
        return v

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            # Validate URL format (only allow safe URLs)
            if not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
                raise ValueError(
                    "avatar_url must be a valid URL starting with http://, https://, or /"
                )
            # Block dangerous protocols
            if v.startswith("javascript:") or v.startswith("data:"):
                raise ValueError("Invalid URL protocol")
        return v


class UserResponse(UserBase):
    id: UUID
    role: str
    is_active: bool
    is_verified: bool
    avatar_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# ============== AUTH SCHEMAS ==============
class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    pass


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if is_weak_password(v):
            raise ValueError(
                "Password must be 8+ chars with uppercase, lowercase, number, and special character"
            )
        return v


# ============== PAGINATION ==============
class PaginationParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============== VENDOR SCHEMAS ==============
class VendorBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    business_name: str = Field(..., min_length=2, max_length=255)
    business_type: str
    description: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class VendorCreate(VendorBase):
    @field_validator("business_name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid business name")
        return v


class VendorUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    business_name: str | None = None
    description: str | None = None
    phone: str | None = None
    email: EmailStr | None = None

    @field_validator("business_name", "description")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class VendorResponse(VendorBase):
    id: UUID
    user_id: UUID
    rating: float | None
    total_reviews: int | None
    is_verified: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class VendorPublicResponse(BaseModel):
    id: UUID
    business_name: str
    business_type: str
    description: str | None
    logo_url: str | None
    rating: float | None
    total_reviews: int | None

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# ============== PROPERTY SCHEMAS ==============
class PropertyBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=2, max_length=255)
    slug: str | None = None
    short_description: str | None = None
    description: str | None = None
    property_type: str = "hotel"
    category: str | None = None

    address: str | None = None
    country: str = "Costa Rica"
    province: str | None = None
    region: str | None = None
    city: str | None = None
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    map_address: str | None = None

    cover_image: str | None = None
    images: list[str] | None = []
    videos: list[str] | None = []
    virtual_tour_url: str | None = None

    amenities: list[str] | None = []
    features: list[str] | None = []

    check_in_time: str = "15:00"
    check_out_time: str = "11:00"
    cancellation_policy: str | None = None
    house_rules: str | None = None
    important_info: str | None = None

    min_guests: int = 1
    max_guests: int = 10
    beds: int = 1
    baths: int = 1
    square_meters: int | None = None

    base_price: float = 0
    currency: str = "USD"
    weekend_price: float = 0
    weekly_discount: float = 0

    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] | None = []

    @field_validator("name", "address", "slug")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class PropertyCreate(PropertyBase):
    rooms: list[dict] | None = []
    pricing_rules: list[dict] | None = []


class PropertyUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    slug: str | None = None
    short_description: str | None = None
    description: str | None = None
    property_type: str | None = None
    category: str | None = None
    address: str | None = None
    country: str | None = None
    province: str | None = None
    region: str | None = None
    city: str | None = None
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    map_address: str | None = None
    cover_image: str | None = None
    images: list[str] | None = None
    videos: list[str] | None = None
    virtual_tour_url: str | None = None
    amenities: list[str] | None = None
    features: list[str] | None = None
    check_in_time: str | None = None
    check_out_time: str | None = None
    cancellation_policy: str | None = None
    house_rules: str | None = None
    important_info: str | None = None
    min_guests: int | None = None
    max_guests: int | None = None
    beds: int | None = None
    baths: int | None = None
    square_meters: int | None = None
    base_price: float | None = None
    weekend_price: float | None = None
    weekly_discount: float | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] | None = None
    is_featured: bool | None = None
    is_active: bool | None = None
    is_verified: bool | None = None

    @field_validator("name", "description", "address")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class RoomSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    property_id: UUID
    name: str
    description: str | None = None
    max_guests: int = 2
    beds: int = 1
    bed_type: str | None = None
    price_per_night: float = 0
    weekend_price: float = 0
    extra_guest_price: float = 0
    cleaning_fee: float = 0
    images: list[str] = []
    is_available: bool = True


class PropertyResponse(PropertyBase):
    id: UUID
    vendor_id: UUID
    rating: float | None = 0.0
    total_reviews: int = 0
    total_bookings: int = 0
    is_featured: bool = False
    is_active: bool = True
    is_verified: bool = False
    rooms: list[RoomSchema] = []
    vendor: VendorPublicResponse | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class PropertyListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    name: str
    slug: str
    short_description: str | None = None
    property_type: str
    category: str | None = None
    city: str | None = None
    region: str | None = None
    province: str | None = None
    cover_image: str | None = None
    rating: float | None = 0.0
    total_reviews: int = 0
    base_price: float = 0
    is_active: bool = True


# ============== TOUR SCHEMAS ==============
class TourBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    category: str
    location: str

    @field_validator("name", "location")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid input")
        return v


class TourCreate(TourBase):
    duration_hours: float
    difficulty: str = "easy"
    meeting_point: str | None = None
    max_group_size: int = 20
    price: float


class TourUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    description: str | None = None
    category: str | None = None
    difficulty: str | None = None
    location: str | None = None
    duration_hours: float | None = None
    duration_text: str | None = None
    meeting_point: str | None = None
    max_group_size: int | None = None
    min_age: int | None = None
    price: float | None = None
    currency: str | None = None
    included: list[str] | None = None
    not_included: list[str] | None = None
    itinerary: list[dict] | None = None
    images: list[str] | None = None
    cover_image: str | None = None
    schedule_days: list[str] | None = None
    is_featured: bool | None = None
    is_active: bool | None = None

    @field_validator("name", "description", "location")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class TourResponse(TourBase):
    id: UUID
    vendor_id: UUID
    slug: str
    duration_hours: float
    duration_text: str | None = None
    difficulty: str
    location: str | None = None
    meeting_point: str | None = None
    price: float
    currency: str = "USD"
    rating: float | None = None
    total_reviews: int | None = None
    is_active: bool
    is_featured: bool = False
    max_group_size: int = 15
    min_age: int = 0
    included: list = []
    not_included: list = []
    itinerary: list = []
    images: list = []
    cover_image: str | None = None
    schedule_days: list = []
    created_at: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class TourListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: UUID
    name: str
    slug: str
    category: str
    difficulty: str
    duration_hours: float
    location: str | None = None
    price: float
    rating: float | None = None
    cover_image: str | None = None
    is_featured: bool = False


# ============== BOOKING SCHEMAS ==============
class BookingBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    guest_name: str = Field(..., min_length=2, max_length=255)
    guest_email: EmailStr
    guest_phone: str | None = None
    guest_notes: str | None = None

    @field_validator("guest_name")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid guest name")
        return v


class BookingPropertyRequest(BookingBase):
    property_id: UUID
    room_id: UUID | None = None
    check_in: datetime
    check_out: datetime
    guests: int = Field(1, ge=1)


class BookingTourRequest(BookingBase):
    tour_id: UUID
    booking_date: datetime
    participants: int = Field(1, ge=1)


class BookingUpdateStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str


class PricePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_id: UUID
    check_in: datetime
    check_out: datetime
    guests: int = Field(1, ge=1)


class PricePreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nights: int
    weekday_nights: int
    weekend_nights: int
    weekday_price: float
    weekend_price: float
    weekday_total: float
    weekend_total: float
    base_subtotal: float
    guests: int
    max_occupancy: int
    extra_guests: int
    extra_guest_price: float
    extra_guests_total: float
    weekly_discount_percent: float = 0
    weekly_discount_amount: float = 0
    subtotal: float
    commission_amount: float
    total: float
    currency: str


class BookingResponse(BookingBase):
    id: UUID
    user_id: UUID | None
    vendor_id: UUID | None
    property_id: UUID | None
    room_id: UUID | None
    tour_id: UUID | None
    booking_type: str
    status: str
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# ============== BLOG SCHEMAS ==============
class BlogPostBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=5, max_length=255)
    excerpt: str | None = None
    content: str = Field(..., min_length=50)
    category: str | None = None

    @field_validator("title", "content")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid input")
        return v


class BlogPostCreate(BlogPostBase):
    featured_image: str | None = None
    tags: list[str] | None = None


class BlogPostUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = None
    excerpt: str | None = None
    content: str | None = None
    featured_image: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    published_at: datetime | None = None
    seo_title: str | None = None
    seo_description: str | None = None

    @field_validator("title", "content")
    @classmethod
    def sanitize_input(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class BlogPostResponse(BlogPostBase):
    id: UUID
    slug: str
    author_id: UUID | None
    status: str
    views_count: int
    is_featured: bool
    featured_image: str | None = None
    tags: list[str] | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    published_at: datetime | None
    created_at: datetime
    author_name: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class BlogPostListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    slug: str
    title: str
    excerpt: str | None
    category: str | None
    status: str
    views_count: int
    is_featured: bool


# ============== DESTINATION SCHEMAS ==============
class DestinationBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=2, max_length=255)
    slug: str | None = None
    description: str | None = None
    country: str = "Costa Rica"
    region: str | None = None
    province: str | None = None
    canton: str | None = None
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    zoom: int = 10
    highlights: list[str] = []
    things_to_do: list[str] = []
    culture: str | None = None
    gastronomy: str | None = None
    history: str | None = None
    best_time: str | None = None
    weather_info: str | None = None
    getting_there: str | None = None
    local_tips: str | None = None
    safety_info: str | None = None
    language: str | None = None
    currency: str | None = None
    timezone: str | None = None
    phone_code: str | None = None
    visa_info: str | None = None
    emergency_numbers: list[str] = []
    image: str | None = None
    gallery: list[str] = []
    videos: list[str] = []
    featured_photo: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] = []
    is_featured: bool = False
    is_active: bool = True
    order: int = 0

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid name")
        return v

    @field_validator(
        "description",
        "culture",
        "gastronomy",
        "history",
        "best_time",
        "weather_info",
        "getting_there",
        "local_tips",
        "safety_info",
        "visa_info",
    )
    @classmethod
    def sanitize_text(cls, v: str | None) -> str | None:
        if v:
            v = sanitize_html(v).strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float | None) -> float | None:
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float | None) -> float | None:
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("zoom")
    @classmethod
    def validate_zoom(cls, v: int) -> int:
        if v < 1 or v > 20:
            raise ValueError("Zoom must be between 1 and 20")
        return v

    @field_validator("image", "featured_photo")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
                raise ValueError("Must be a valid URL (http://, https://, or relative)")
        return v

    @field_validator("phone_code")
    @classmethod
    def validate_phone_code(cls, v: str | None) -> str | None:
        if v and not re.match(r"^\+?\d{1,6}$", v):
            raise ValueError("Invalid phone code format (e.g., +506)")
        return v


class DestinationCreate(DestinationBase):
    pass


class DestinationUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    country: str | None = None
    region: str | None = None
    province: str | None = None
    canton: str | None = None
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    zoom: int | None = None
    highlights: list[str] | None = None
    things_to_do: list[str] | None = None
    culture: str | None = None
    gastronomy: str | None = None
    history: str | None = None
    best_time: str | None = None
    weather_info: str | None = None
    getting_there: str | None = None
    local_tips: str | None = None
    safety_info: str | None = None
    language: str | None = None
    currency: str | None = None
    timezone: str | None = None
    phone_code: str | None = None
    visa_info: str | None = None
    emergency_numbers: list[str] | None = None
    image: str | None = None
    gallery: list[str] | None = None
    videos: list[str] | None = None
    featured_photo: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] | None = None
    is_featured: bool | None = None
    is_active: bool | None = None
    order: int | None = None

    @field_validator("name", "description", "culture", "gastronomy", "history")
    @classmethod
    def sanitize_update_input(cls, v: str | None) -> str | None:
        if v:
            v = sanitize_html(v).strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_update_latitude(cls, v: float | None) -> float | None:
        if v is not None and (v < -90 or v > 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_update_longitude(cls, v: float | None) -> float | None:
        if v is not None and (v < -180 or v > 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v

    @field_validator("zoom")
    @classmethod
    def validate_update_zoom(cls, v: int | None) -> int | None:
        if v is not None and (v < 1 or v > 20):
            raise ValueError("Zoom must be between 1 and 20")
        return v

    @field_validator("image", "featured_photo")
    @classmethod
    def validate_update_url(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if not (v.startswith("http://") or v.startswith("https://") or v.startswith("/")):
                raise ValueError("Must be a valid URL (http://, https://, or relative)")
        return v

    @field_validator("phone_code")
    @classmethod
    def validate_update_phone_code(cls, v: str | None) -> str | None:
        if v and not re.match(r"^\+?\d{1,6}$", v):
            raise ValueError("Invalid phone code format (e.g., +506)")
        return v


class DestinationResponse(DestinationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    highlights: list[str] | None = None
    things_to_do: list[str] | None = None
    emergency_numbers: list[str] | None = None
    gallery: list[str] | None = None
    videos: list[str] | None = None
    seo_keywords: list[str] | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    @field_validator(
        "highlights",
        "things_to_do",
        "emergency_numbers",
        "gallery",
        "videos",
        "seo_keywords",
        mode="before",
    )
    @classmethod
    def list_default(cls, v):
        return v if v is not None else []


# ============== NEWSLETTER SCHEMAS ==============
class NewsletterSubscribe(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    first_name: str | None = Field(None, max_length=100)

    @field_validator("first_name")
    @classmethod
    def sanitize_name(cls, v: str | None) -> str | None:
        if v is not None:
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
            return sanitize_html(v)
        return v


class NewsletterSubscribeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    success: bool
    message: str


class NewsletterSubscriberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    email: str
    first_name: str | None
    is_active: bool
    is_confirmed: bool
    source: str
    created_at: datetime
