"""Factory helpers for generating test data.

Reduces boilerplate in test files — each factory returns a plain dict
that can be passed directly to API endpoints or model constructors.
"""

from datetime import datetime, timedelta
from uuid import uuid4


def user_data(
    email: str | None = None,
    role: str = "client",
    password: str = "TestPass123!",
    full_name: str | None = None,
    phone: str | None = None,
) -> dict:
    return {
        "email": email or f"test_{uuid4().hex[:8]}@example.com",
        "password": password,
        "full_name": full_name or "Test User",
        "phone": phone or "+50688888888",
        "role": role,
    }


def vendor_data(
    business_name: str | None = None,
    business_type: str = "hotel",
    description: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> dict:
    return {
        "business_name": business_name or f"Test Vendor {uuid4().hex[:6]}",
        "business_type": business_type,
        "description": description or "A test vendor for integration testing",
        "phone": phone or "+50688888888",
        "email": email or f"vendor_{uuid4().hex[:8]}@example.com",
    }


def property_data(
    name: str | None = None,
    property_type: str = "hotel",
    base_price: float = 150.0,
    **overrides,
) -> dict:
    data = {
        "name": name or f"Test Property {uuid4().hex[:6]}",
        "property_type": property_type,
        "description": "A beautiful test property with ocean views.",
        "base_price": base_price,
        "currency": "USD",
        "country": "Costa Rica",
        "province": "San Jose",
        "max_guests": 4,
        "beds": 2,
        "baths": 1,
    }
    data.update(overrides)
    return data


def tour_data(
    name: str | None = None,
    category: str = "adventure",
    price: float = 75.0,
    duration_hours: float = 4.0,
    **overrides,
) -> dict:
    data = {
        "name": name or f"Test Tour {uuid4().hex[:6]}",
        "category": category,
        "description": "An exciting test tour.",
        "location": "San Jose",
        "price": price,
        "duration_hours": duration_hours,
        "difficulty": "easy",
        "max_group_size": 15,
    }
    data.update(overrides)
    return data


def booking_data(
    booking_type: str = "property",
    check_in: str | None = None,
    check_out: str | None = None,
    **overrides,
) -> dict:
    now = datetime.utcnow()
    data = {
        "guest_name": "Test Booker",
        "guest_email": "booker@example.com",
        "guest_phone": "+50688888888",
        "booking_type": booking_type,
    }
    if booking_type == "property":
        data["check_in"] = check_in or (now + timedelta(days=7)).isoformat()
        data["check_out"] = check_out or (now + timedelta(days=10)).isoformat()
        data["guests"] = 2
    else:
        data["booking_date"] = check_in or (now + timedelta(days=14)).isoformat()
        data["participants"] = 2
    data.update(overrides)
    return data


def destination_data(
    name: str | None = None,
    region: str = "San Jose",
    **overrides,
) -> dict:
    data = {
        "name": name or f"Test Destination {uuid4().hex[:6]}",
        "region": region,
        "country": "Costa Rica",
        "description": "A beautiful test destination.",
        "is_active": True,
    }
    data.update(overrides)
    return data


def blog_data(
    title: str | None = None,
    content: str | None = None,
    **overrides,
) -> dict:
    data = {
        "title": title or f"Test Blog Post {uuid4().hex[:6]}",
        "content": content
        or "This is a test blog post with enough content to pass validation. " * 5,
        "category": "travel",
        "status": "draft",
    }
    data.update(overrides)
    return data


def media_file_data(
    filename: str = "test_image.webp",
    mime_type: str = "image/webp",
    size_bytes: int = 10240,
    **overrides,
) -> dict:
    data = {
        "filename": filename,
        "original_name": filename,
        "mime_type": mime_type,
        "size_bytes": size_bytes,
        "url": f"https://res.cloudinary.com/mock/uploads/{filename}",
    }
    data.update(overrides)
    return data


def vehicle_data(
    name: str | None = None,
    vehicle_type: str = "sedan",
    **overrides,
) -> dict:
    data = {
        "name": name or f"Test Vehicle {uuid4().hex[:6]}",
        "vehicle_type": vehicle_type,
        "description": "A comfortable test vehicle.",
        "capacity": 4,
        "price_per_day": 50.0,
    }
    data.update(overrides)
    return data
