"""
Slug utilities - Genera slugs SEO-friendly con soporte para español/francés
"""
import uuid
from slugify import slugify


def generate_slug(text: str, max_length: int = 100, suffix: bool = True) -> str:
    """
    Generate a URL-friendly slug from text.
    
    Features:
    - Handles Spanish/French characters (ñ, tildes, cedillas)
    - Removes special characters
    - Adds unique suffix if requested
    - Truncates to max_length
    
    Examples:
        "Hotel Paraíso" -> "hotel-paraiso-a1b2c3d4"
        "Montaña Verde" -> "montana-verde-e5f6g7h8"
        "Café & Restaurante" -> "cafe-restaurante-i9j0k1l2"
    """
    if not text:
        return ""
    
    # Generate base slug using python-slugify
    # separator='-' ensures consistent hyphen separation
    # lowercase=True ensures lowercase output
    base_slug = slugify(
        text,
        separator='-',
        lowercase=True,
        max_length=max_length - 9 if suffix else max_length,  # Reserve space for suffix
        word_boundary=True,
        save_order=True
    )
    
    if not base_slug:
        base_slug = "item"
    
    # Add unique suffix if requested
    if suffix:
        unique_suffix = uuid.uuid4().hex[:8]
        return f"{base_slug}-{unique_suffix}"
    
    return base_slug


def generate_vendor_slug(business_name: str) -> str:
    """
    Generate a slug for vendor business names.
    Keeps it readable while ensuring uniqueness.
    """
    return generate_slug(business_name, max_length=150, suffix=True)


def generate_property_slug(name: str, city: str = None) -> str:
    """
    Generate a slug for properties.
    Optionally includes city for better SEO.
    """
    if city:
        text = f"{name} {city}"
    else:
        text = name
    return generate_slug(text, max_length=150, suffix=True)


def generate_tour_slug(name: str, location: str = None) -> str:
    """
    Generate a slug for tours.
    Optionally includes location for better SEO.
    """
    if location:
        text = f"{name} {location}"
    else:
        text = name
    return generate_slug(text, max_length=150, suffix=True)


def sanitize_existing_slug(slug: str) -> str:
    """
    Sanitize an existing slug.
    Useful for cleaning up manually entered slugs.
    """
    if not slug:
        return ""
    
    # Re-slugify to ensure consistency
    return slugify(
        slug,
        separator='-',
        lowercase=True,
        max_length=150
    )
