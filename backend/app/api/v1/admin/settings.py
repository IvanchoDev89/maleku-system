from datetime import datetime, timezone
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models import User, UserRole

router = APIRouter()


class SettingsResponse(BaseModel):
    """Generic settings response wrapper"""

    pass


class SettingDetailResponse(BaseModel):
    key: str
    value: Any
    category: str
    description: Optional[str] = None
    is_public: bool = False
    updated_at: datetime


class UpdateSettingResponse(BaseModel):
    message: str
    key: str
    value: Any


class BulkUpdateResponse(BaseModel):
    message: str
    updated: list[str]


class CategoriesResponse(BaseModel):
    categories: list[str]


# Settings Model
class SystemSetting(BaseModel):
    key: str
    value: Any
    category: str
    description: Optional[str] = None
    is_public: bool = False
    updated_at: datetime


def validate_setting_value(key: str, value: Any) -> tuple[bool, str]:
    """Validate setting value based on key type"""
    if key not in DEFAULT_SETTINGS:
        return False, f"Unknown setting key: {key}"

    # Handle None values
    if value is None:
        return True, None

    # Type validation
    if key in [
        "site_name",
        "site_description",
        "site_keywords",
        "site_logo",
        "site_favicon",
    ]:
        if not isinstance(value, str):
            return False, f"{key} must be a string"

    elif key in ["contact_email", "contact_address"]:
        if not isinstance(value, str):
            return False, f"{key} must be a string"

    elif key in ["contact_phone", "contact_whatsapp"]:
        if not isinstance(value, str):
            return False, f"{key} must be a string"

    elif key in ["commission_rate", "tax_rate", "min_booking_amount"]:
        if not isinstance(value, (int, float)):
            return False, f"{key} must be a number"
        if value < 0:
            return False, f"{key} cannot be negative"

    elif key in ["currency", "currency_symbol"]:
        if not isinstance(value, str):
            return False, f"{key} must be a string"

    elif key in [
        "social_facebook",
        "social_instagram",
        "social_twitter",
        "social_youtube",
        "social_tiktok",
    ]:
        if value and not isinstance(value, str):
            return False, f"{key} must be a string"
        # Validate URL format for social links
        if value and not (
            value.startswith("http://") or value.startswith("https://") or value == ""
        ):
            return False, f"{key} must be a valid URL"

    elif key in ["booking_cancellation_hours", "booking_refund_percentage"]:
        if not isinstance(value, int):
            return False, f"{key} must be an integer"
        if value < 0:
            return False, f"{key} cannot be negative"

    elif key in ["seo_robots"]:
        if not isinstance(value, str):
            return False, f"{key} must be a string"
        # Validate robots directive
        allowed = ["index", "noindex", "follow", "nofollow"]
        directives = [d.strip() for d in value.split(",")]
        for d in directives:
            if d not in allowed:
                return False, f"Invalid robots directive: {d}"

    elif key in ["languages_enabled"]:
        if not isinstance(value, list):
            return False, f"{key} must be a list"
        for lang in value:
            if lang not in ["es", "en", "fr", "de", "pt"]:
                return False, f"Invalid language code: {lang}"

    elif key in ["theme_primary_color", "theme_secondary_color", "theme_accent_color"]:
        if not isinstance(value, str):
            return False, f"{key} must be a string"
        # Validate hex color format
        if not (value.startswith("#") and len(value) in [4, 7]):
            return False, f"{key} must be a valid hex color (e.g., #1e7a67)"

    elif key in [
        "maintenance_mode",
        "theme_dark_mode",
        "feature_blog_enabled",
        "feature_reviews_enabled",
        "feature_newsletter_enabled",
        "feature_multilingual",
        "booking_confirmation_required",
        "email_welcome_enabled",
    ]:
        if not isinstance(value, bool):
            return False, f"{key} must be a boolean"

    elif key in ["email_smtp_port"]:
        if not isinstance(value, int):
            return False, f"{key} must be an integer"
        if value < 1 or value > 65535:
            return False, f"{key} must be a valid port (1-65535)"

    elif key in ["default_language"]:
        if value not in ["es", "en", "fr", "de", "pt"]:
            return False, f"Invalid default language: {value}"

    return True, None


# Default system settings
DEFAULT_SETTINGS = {
    # General
    "site_name": {
        "value": "Costa Rica Travel",
        "category": "general",
        "description": "Nombre del sitio",
        "is_public": True,
    },
    "site_description": {
        "value": "Descubre Costa Rica: hoteles, tours y experiencias únicas",
        "category": "general",
        "description": "Descripción del sitio",
        "is_public": True,
    },
    "site_keywords": {
        "value": "Costa Rica, turismo, viajes, hoteles, tours",
        "category": "general",
        "description": "Palabras clave SEO",
        "is_public": True,
    },
    "site_logo": {
        "value": "/logo.svg",
        "category": "general",
        "description": "Logo del sitio",
        "is_public": True,
    },
    "site_favicon": {
        "value": "/favicon.svg",
        "category": "general",
        "description": "Favicon",
        "is_public": True,
    },
    # Contact
    "contact_email": {
        "value": "info@costaricatravel.dev",
        "category": "contact",
        "description": "Email de contacto",
        "is_public": True,
    },
    "contact_phone": {
        "value": "+50688888888",
        "category": "contact",
        "description": "Teléfono de contacto",
        "is_public": True,
    },
    "contact_address": {
        "value": "San José, Costa Rica",
        "category": "contact",
        "description": "Dirección",
        "is_public": True,
    },
    "contact_whatsapp": {
        "value": "+50688888888",
        "category": "contact",
        "description": "WhatsApp",
        "is_public": True,
    },
    # Social
    "social_facebook": {
        "value": "https://facebook.com/costaricatravel",
        "category": "social",
        "description": "Facebook",
        "is_public": True,
    },
    "social_instagram": {
        "value": "https://instagram.com/costaricatravel",
        "category": "social",
        "description": "Instagram",
        "is_public": True,
    },
    "social_twitter": {
        "value": "https://twitter.com/costaricatravel",
        "category": "social",
        "description": "Twitter",
        "is_public": True,
    },
    "social_youtube": {
        "value": "",
        "category": "social",
        "description": "YouTube",
        "is_public": True,
    },
    "social_tiktok": {
        "value": "",
        "category": "social",
        "description": "TikTok",
        "is_public": True,
    },
    # Business
    "commission_rate": {
        "value": 10,
        "category": "business",
        "description": "Porcentaje de comisión",
        "is_public": False,
    },
    "currency": {
        "value": "USD",
        "category": "business",
        "description": "Moneda principal",
        "is_public": True,
    },
    "currency_symbol": {
        "value": "$",
        "category": "business",
        "description": "Símbolo de moneda",
        "is_public": True,
    },
    "tax_rate": {
        "value": 0,
        "category": "business",
        "description": "Tasa de impuesto (%)",
        "is_public": False,
    },
    "min_booking_amount": {
        "value": 10,
        "category": "business",
        "description": "Monto mínimo de reserva",
        "is_public": False,
    },
    # Email
    "email_from_name": {
        "value": "Costa Rica Travel",
        "category": "email",
        "description": "Nombre del remitente",
        "is_public": False,
    },
    "email_from_email": {
        "value": "noreply@costaricatravel.dev",
        "category": "email",
        "description": "Email del remitente",
        "is_public": False,
    },
    "email_smtp_host": {
        "value": "",
        "category": "email",
        "description": "Servidor SMTP",
        "is_public": False,
    },
    "email_smtp_port": {
        "value": 587,
        "category": "email",
        "description": "Puerto SMTP",
        "is_public": False,
    },
    "email_smtp_user": {
        "value": "",
        "category": "email",
        "description": "Usuario SMTP",
        "is_public": False,
    },
    "email_smtp_password": {
        "value": "",
        "category": "email",
        "description": "Contraseña SMTP",
        "is_public": False,
    },
    "email_welcome_enabled": {
        "value": True,
        "category": "email",
        "description": "Enviar email de bienvenida",
        "is_public": False,
    },
    # Booking
    "booking_confirmation_required": {
        "value": True,
        "category": "booking",
        "description": "Confirmación manual requerida",
        "is_public": False,
    },
    "booking_cancellation_hours": {
        "value": 24,
        "category": "booking",
        "description": "Horas antes para cancelar",
        "is_public": True,
    },
    "booking_refund_percentage": {
        "value": 100,
        "category": "booking",
        "description": "% de reembolso si cancela a tiempo",
        "is_public": True,
    },
    # SEO
    "seo_og_image": {
        "value": "/images/og-default.jpg",
        "category": "seo",
        "description": "Imagen OG por defecto",
        "is_public": True,
    },
    "seo_robots": {
        "value": "index, follow",
        "category": "seo",
        "description": "Directivas robots",
        "is_public": True,
    },
    "seo_google_analytics_id": {
        "value": "",
        "category": "seo",
        "description": "Google Analytics ID",
        "is_public": False,
    },
    "seo_google_search_console": {
        "value": "",
        "category": "seo",
        "description": "Verificación Search Console",
        "is_public": False,
    },
    # Maintenance
    "maintenance_mode": {
        "value": False,
        "category": "maintenance",
        "description": "Modo mantenimiento",
        "is_public": False,
    },
    "maintenance_message": {
        "value": "Site en mantenimiento. Volvemos pronto.",
        "category": "maintenance",
        "description": "Mensaje de mantenimiento",
        "is_public": True,
    },
    # Features
    "feature_blog_enabled": {
        "value": True,
        "category": "features",
        "description": "Blog habilitado",
        "is_public": True,
    },
    "feature_reviews_enabled": {
        "value": True,
        "category": "features",
        "description": "Reseñas habilitadas",
        "is_public": True,
    },
    "feature_newsletter_enabled": {
        "value": True,
        "category": "features",
        "description": "Newsletter habilitado",
        "is_public": True,
    },
    "feature_multilingual": {
        "value": True,
        "category": "features",
        "description": "Multilenguaje habilitado",
        "is_public": True,
    },
    # Languages
    "languages_enabled": {
        "value": ["es", "en", "fr"],
        "category": "languages",
        "description": "Idiomas habilitados",
        "is_public": True,
    },
    "default_language": {
        "value": "es",
        "category": "languages",
        "description": "Idioma por defecto",
        "is_public": True,
    },
    # Appearance
    "theme_primary_color": {
        "value": "#1e7a67",
        "category": "appearance",
        "description": "Color primario",
        "is_public": True,
    },
    "theme_secondary_color": {
        "value": "#2a9d8f",
        "category": "appearance",
        "description": "Color secundario",
        "is_public": True,
    },
    "theme_accent_color": {
        "value": "#e76f51",
        "category": "appearance",
        "description": "Color de acento",
        "is_public": True,
    },
    "theme_dark_mode": {
        "value": False,
        "category": "appearance",
        "description": "Modo oscuro por defecto",
        "is_public": True,
    },
    "theme_font_family": {
        "value": "Outfit",
        "category": "appearance",
        "description": "Familia de fuente",
        "is_public": True,
    },
}

# In-memory storage (use database in production)
settings_cache = {}


def get_setting(key: str, default: Any = None) -> Any:
    if key in settings_cache:
        return settings_cache[key]["value"]
    if key in DEFAULT_SETTINGS:
        return DEFAULT_SETTINGS[key]["value"]
    return default


def set_setting(key: str, value: Any) -> None:
    if key in DEFAULT_SETTINGS:
        settings_cache[key] = {
            "value": value,
            "category": DEFAULT_SETTINGS[key]["category"],
            "description": DEFAULT_SETTINGS[key]["description"],
            "is_public": DEFAULT_SETTINGS[key]["is_public"],
            "updated_at": datetime.now(timezone.utc),
        }


# Initialize default settings
for key, config in DEFAULT_SETTINGS.items():
    settings_cache[key] = {
        "value": config["value"],
        "category": config["category"],
        "description": config["description"],
        "is_public": config["is_public"],
        "updated_at": datetime.now(timezone.utc),
    }


@router.get("", response_model=dict)
async def get_all_settings(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Group by category
    result = {}
    for key, data in settings_cache.items():
        category = data["category"]
        if category not in result:
            result[category] = {}
        result[category][key] = data

    return result


@router.get("/public", response_model=dict)
async def get_public_settings():
    """Get public settings for frontend"""
    result = {}
    for key, data in settings_cache.items():
        if data["is_public"]:
            result[key] = data["value"]
    return result


@router.get("/{key}", response_model=SettingDetailResponse)
async def get_setting_by_key(key: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    if key not in settings_cache:
        raise HTTPException(status_code=404, detail="Setting not found")

    return settings_cache[key]


@router.put("/{key}", response_model=UpdateSettingResponse)
async def update_setting(
    key: str, value: Any, current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403, detail="Only super admin can update settings"
        )

    if key not in DEFAULT_SETTINGS:
        raise HTTPException(status_code=404, detail="Setting key not found")

    # Validate value type
    is_valid, error_msg = validate_setting_value(key, value)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    settings_cache[key] = {
        "value": value,
        "category": DEFAULT_SETTINGS[key]["category"],
        "description": DEFAULT_SETTINGS[key]["description"],
        "is_public": DEFAULT_SETTINGS[key]["is_public"],
        "updated_at": datetime.now(timezone.utc),
    }

    return {"message": "Setting updated", "key": key, "value": value}


@router.post("/bulk", response_model=BulkUpdateResponse)
async def bulk_update_settings(
    settings: dict, current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=403, detail="Only super admin can update settings"
        )

    # Validate all settings first
    errors = {}
    for key, value in settings.items():
        if key in DEFAULT_SETTINGS:
            is_valid, error_msg = validate_setting_value(key, value)
            if not is_valid:
                errors[key] = error_msg

    if errors:
        raise HTTPException(status_code=400, detail={"validation_errors": errors})

    # All validations passed, update settings
    updated = []
    for key, value in settings.items():
        if key in DEFAULT_SETTINGS:
            settings_cache[key] = {
                "value": value,
                "category": DEFAULT_SETTINGS[key]["category"],
                "description": DEFAULT_SETTINGS[key]["description"],
                "is_public": DEFAULT_SETTINGS[key]["is_public"],
                "updated_at": datetime.now(timezone.utc),
            }
            updated.append(key)

    return {"message": f"Updated {len(updated)} settings", "updated": updated}


@router.get("/categories/list", response_model=CategoriesResponse)
async def get_categories(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    categories = list(set(config["category"] for config in DEFAULT_SETTINGS.values()))
    return {"categories": categories}
