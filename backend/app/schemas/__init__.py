from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID
import re


def sanitize_slug(value: str) -> str:
    """Remove dangerous characters from slug"""
    return re.sub(r"[^a-z0-9\-]", "", value.lower().replace(" ", "-"))


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


def is_weak_password(value: str) -> bool:
    """Check password strength"""
    if len(value) < 8:
        return True
    if not re.search(r"[A-Z]", value):
        return True
    if not re.search(r"[a-z]", value):
        return True
    if not re.search(r"[0-9]", value):
        return True
    return False


# ============== USER SCHEMAS ==============
class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)

    @field_validator("full_name", "phone")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
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
        if is_weak_password(v):
            raise ValueError(
                "Password must be 8+ chars with uppercase, lowercase, and numbers"
            )
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, min_length=8, max_length=20)
    avatar_url: Optional[str] = None

    @field_validator("full_name", "phone")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid characters in input")
        return v

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            # Validate URL format (only allow safe URLs)
            if not (
                v.startswith("http://") or v.startswith("https://") or v.startswith("/")
            ):
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
    avatar_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== AUTH SCHEMAS ==============
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(UserCreate):
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if is_weak_password(v):
            raise ValueError(
                "Password must be 8+ chars with uppercase, lowercase, and numbers"
            )
        return v


# ============== PAGINATION ==============
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ============== VENDOR SCHEMAS ==============
class VendorBase(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=255)
    business_type: str
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class VendorCreate(VendorBase):
    @field_validator("business_name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid business name")
        return v


class VendorUpdate(BaseModel):
    business_name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

    @field_validator("business_name", "description")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class VendorResponse(VendorBase):
    id: UUID
    user_id: UUID
    rating: Optional[float]
    total_reviews: Optional[int]
    is_verified: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VendorPublicResponse(BaseModel):
    id: UUID
    business_name: str
    business_type: str
    description: Optional[str]
    logo_url: Optional[str]
    rating: Optional[float]
    total_reviews: Optional[int]

    model_config = ConfigDict(from_attributes=True)


# ============== PROPERTY SCHEMAS ==============
class PropertyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    property_type: str = "hotel"
    category: Optional[str] = None

    address: Optional[str] = None
    country: str = "Costa Rica"
    province: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    map_address: Optional[str] = None

    cover_image: Optional[str] = None
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    virtual_tour_url: Optional[str] = None

    amenities: Optional[List[str]] = []
    features: Optional[List[str]] = []

    check_in_time: str = "15:00"
    check_out_time: str = "11:00"
    cancellation_policy: Optional[str] = None
    house_rules: Optional[str] = None
    important_info: Optional[str] = None

    min_guests: int = 1
    max_guests: int = 10
    beds: int = 1
    baths: int = 1
    square_meters: Optional[int] = None

    base_price: float = 0
    currency: str = "USD"
    weekend_price: float = 0
    weekly_discount: float = 0

    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = []
    seo_slug: Optional[str] = None

    @field_validator("name", "address", "slug")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class PropertyCreate(PropertyBase):
    rooms: Optional[List[dict]] = []
    pricing_rules: Optional[List[dict]] = []


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    map_address: Optional[str] = None
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    virtual_tour_url: Optional[str] = None
    amenities: Optional[List[str]] = None
    features: Optional[List[str]] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    cancellation_policy: Optional[str] = None
    house_rules: Optional[str] = None
    important_info: Optional[str] = None
    min_guests: Optional[int] = None
    max_guests: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[int] = None
    square_meters: Optional[int] = None
    base_price: Optional[float] = None
    weekend_price: Optional[float] = None
    weekly_discount: Optional[float] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    seo_slug: Optional[str] = None

    @field_validator("name", "description", "address")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class PropertyResponse(PropertyBase):
    id: UUID
    vendor_id: UUID
    rating: Optional[float] = 0.0
    total_reviews: int = 0
    total_bookings: int = 0
    is_featured: bool = False
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PropertyListResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    short_description: Optional[str] = None
    property_type: str
    category: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    province: Optional[str] = None
    cover_image: Optional[str] = None
    rating: Optional[float] = 0.0
    total_reviews: int = 0
    base_price: float = 0
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# ============== TOUR SCHEMAS ==============
class TourBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
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
    meeting_point: Optional[str] = None
    max_group_size: int = 20
    price: float


class TourUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

    @field_validator("name", "description", "location")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class TourResponse(TourBase):
    id: UUID
    vendor_id: UUID
    duration_hours: float
    difficulty: str
    location: str
    rating: Optional[float]
    total_reviews: Optional[int]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TourListResponse(BaseModel):
    id: UUID
    name: str
    category: str
    difficulty: str
    duration_hours: float
    location: str
    price: float
    rating: Optional[float]

    model_config = ConfigDict(from_attributes=True)


# ============== BOOKING SCHEMAS ==============
class BookingBase(BaseModel):
    guest_name: str = Field(..., min_length=2, max_length=255)
    guest_email: EmailStr
    guest_phone: Optional[str] = None
    guest_notes: Optional[str] = None

    @field_validator("guest_name")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid guest name")
        return v


class BookingPropertyRequest(BookingBase):
    property_id: UUID
    room_id: Optional[UUID] = None
    check_in: datetime
    check_out: datetime
    guests: int = Field(1, ge=1)


class BookingTourRequest(BookingBase):
    tour_id: UUID
    booking_date: datetime
    participants: int = Field(1, ge=1)


class BookingUpdateStatus(BaseModel):
    status: str


class PricePreviewRequest(BaseModel):
    """Request to preview pricing before booking"""

    room_id: UUID
    check_in: datetime
    check_out: datetime
    guests: int = Field(1, ge=1)


class PricePreviewResponse(BaseModel):
    """Detailed price breakdown for preview"""

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
    user_id: Optional[UUID]
    vendor_id: Optional[UUID]
    property_id: Optional[UUID]
    room_id: Optional[UUID]
    tour_id: Optional[UUID]
    booking_type: str
    status: str
    total_amount: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== BLOG SCHEMAS ==============
class BlogPostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    excerpt: Optional[str] = None
    content: str = Field(..., min_length=50)
    category: Optional[str] = None

    @field_validator("title", "content")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid input")
        return v


class BlogPostCreate(BlogPostBase):
    featured_image: Optional[str] = None
    tags: Optional[List[str]] = None


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None

    @field_validator("title", "content")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class BlogPostResponse(BlogPostBase):
    id: UUID
    author_id: Optional[UUID]
    status: str
    views_count: int
    is_featured: bool
    published_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlogPostListResponse(BaseModel):
    id: UUID
    title: str
    excerpt: Optional[str]
    category: Optional[str]
    status: str
    views_count: int
    is_featured: bool

    model_config = ConfigDict(from_attributes=True)


# ============== DESTINATION SCHEMAS ==============
class DestinationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        v = v.strip()
        if is_dangerous_sql(v):
            raise ValueError("Invalid name")
        return v


class DestinationCreate(DestinationBase):
    region: str
    province: Optional[str] = None


class DestinationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

    @field_validator("name", "description")
    @classmethod
    def sanitize_input(cls, v: Optional[str]) -> Optional[str]:
        if v:
            v = v.strip()
            if is_dangerous_sql(v):
                raise ValueError("Invalid input")
        return v


class DestinationResponse(DestinationBase):
    id: UUID
    region: str
    province: Optional[str]
    is_featured: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ============== NEWSLETTER SCHEMAS ==============
class NewsletterSubscribe(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)


class NewsletterSubscribeResponse(BaseModel):
    success: bool
    message: str


class NewsletterSubscriberResponse(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    is_active: bool
    is_confirmed: bool
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
