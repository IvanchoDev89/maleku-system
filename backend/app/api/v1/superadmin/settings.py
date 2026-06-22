"""
Super Admin Settings Management API

Global system configuration management for SUPER_ADMIN only.
Handles environment variables, integrations, email templates, and feature flags.
"""

from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Body, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.core.config import settings
from app.models import User
from app.services.audit_service import AuditService
from app.models.audit import AuditAction

router = APIRouter(prefix="/settings", tags=["Super Admin - Settings"])


def _serialize_for_audit(data: dict) -> dict:
    """Convert non-JSON-serializable values (datetime, etc.) to strings."""
    result = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif hasattr(v, "isoformat"):
            result[k] = str(v)
        else:
            result[k] = v
    return result


class SettingsResponse(BaseModel):
    """Public settings response (safe to expose)"""

    site_name: str
    site_url: str
    support_email: str
    default_currency: str
    commission_rate: float
    maintenance_mode: bool
    enable_registration: bool
    require_email_verification: bool
    timezone: str = "America/Costa_Rica"

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    """Settings update request"""

    site_name: Optional[str] = Field(None, max_length=100)
    site_url: Optional[str] = Field(None, max_length=200)
    support_email: Optional[str] = Field(None, max_length=100)
    default_currency: Optional[str] = Field(None, pattern="^(USD|CRC|EUR)$")
    commission_rate: Optional[float] = Field(None, ge=0, le=100)
    maintenance_mode: Optional[bool] = None
    enable_registration: Optional[bool] = None
    require_email_verification: Optional[bool] = None


class IntegrationSettings(BaseModel):
    """Third-party integration settings"""

    stripe_enabled: bool = False
    stripe_publishable_key: str = ""
    stripe_webhook_configured: bool = False

    cloudinary_enabled: bool = False
    cloudinary_cloud_name: str = ""

    sendgrid_enabled: bool = False
    sendgrid_from_email: str = ""

    google_analytics_enabled: bool = False
    google_analytics_id: str = ""


class EmailTemplate(BaseModel):
    """Email template model"""

    id: str
    name: str
    subject: str
    body_html: str
    body_text: str
    variables: List[str]
    last_updated: datetime


class EmailTemplateUpdate(BaseModel):
    """Email template update"""

    subject: str = Field(..., max_length=200)
    body_html: str = Field(..., max_length=10000)
    body_text: Optional[str] = Field(None, max_length=5000)


class FeatureFlag(BaseModel):
    """Feature flag model"""

    name: str
    enabled: bool
    description: str
    rollout_percentage: int = Field(ge=0, le=100)
    updated_at: datetime


# In-memory store for settings (in production, use database)
_system_settings = {
    "site_name": settings.APP_NAME,
    "site_url": "https://costaricatravel.dev",
    "support_email": "support@costaricatravel.dev",
    "default_currency": "USD",
    "commission_rate": 10.0,
    "maintenance_mode": False,
    "enable_registration": True,
    "require_email_verification": True,
    "timezone": "America/Costa_Rica",
}

_email_templates = [
    {
        "id": "welcome",
        "name": "Bienvenida",
        "subject": "Bienvenido a Costa Rica Travel",
        "body_html": "<h1>Bienvenido {{name}}</h1><p>Gracias por registrarte.</p>",
        "body_text": "Bienvenido {{name}}. Gracias por registrarte.",
        "variables": ["name", "email"],
        "last_updated": datetime.now(timezone.utc),
    },
    {
        "id": "booking_confirmation",
        "name": "Confirmación de Reserva",
        "subject": "Tu reserva ha sido confirmada",
        "body_html": "<h1>Reserva Confirmada</h1><p>Hola {{name}}, tu reserva #{{booking_id}} está confirmada.</p>",
        "body_text": "Reserva Confirmada. Hola {{name}}, tu reserva #{{booking_id}} está confirmada.",
        "variables": ["name", "booking_id", "service_name", "date"],
        "last_updated": datetime.now(timezone.utc),
    },
    {
        "id": "password_reset",
        "name": "Restablecer Contraseña",
        "subject": "Solicitud de restablecimiento de contraseña",
        "body_html": "<h1>Restablecer Contraseña</h1><p>Haz clic <a href='{{reset_url}}'>aquí</a> para restablecer.</p>",
        "body_text": "Restablecer Contraseña. Visita: {{reset_url}}",
        "variables": ["reset_url", "expires_in"],
        "last_updated": datetime.now(timezone.utc),
    },
]

_feature_flags = [
    {
        "name": "new_search",
        "enabled": True,
        "description": "Nuevo sistema de búsqueda",
        "rollout_percentage": 100,
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "name": "new_booking_flow",
        "enabled": False,
        "description": "Nuevo flujo de reservas",
        "rollout_percentage": 0,
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "name": "reviews_system",
        "enabled": True,
        "description": "Sistema de reseñas",
        "rollout_percentage": 100,
        "updated_at": datetime.now(timezone.utc),
    },
]


@router.get("", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get current system settings (public safe)"""
    return SettingsResponse(**_system_settings)


@router.put("", response_model=SettingsResponse)
@limiter.limit("10/minute")
async def update_settings(
    request: Request,
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update system settings"""
    old_values = _system_settings.copy()

    allowed_fields = {
        "site_name",
        "site_url",
        "support_email",
        "default_currency",
        "commission_rate",
        "maintenance_mode",
        "enable_registration",
        "require_email_verification",
    }

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in allowed_fields:
            _system_settings[key] = value

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="system_settings",
        old_values=_serialize_for_audit(old_values),
        new_values=_serialize_for_audit(_system_settings),
        changes_summary=f"Settings updated by {current_user.email}",
    )

    return SettingsResponse(**_system_settings)


@router.get("/integrations", response_model=IntegrationSettings)
async def get_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get third-party integration status (masked keys for security)"""
    return IntegrationSettings(
        stripe_enabled=bool(settings.STRIPE_SECRET_KEY),
        stripe_publishable_key=settings.STRIPE_PUBLISHABLE_KEY[:10] + "..."
        if settings.STRIPE_PUBLISHABLE_KEY
        else "",
        stripe_webhook_configured=bool(settings.STRIPE_WEBHOOK_SECRET),
        cloudinary_enabled=bool(settings.CLOUDINARY_CLOUD_NAME),
        cloudinary_cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        sendgrid_enabled=False,  # Add to settings later
        sendgrid_from_email="",
        google_analytics_enabled=False,
        google_analytics_id="",
    )


@router.get("/email-templates", response_model=List[EmailTemplate])
async def get_email_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get all email templates"""
    return [EmailTemplate(**t) for t in _email_templates]


@router.get("/email-templates/{template_id}", response_model=EmailTemplate)
async def get_email_template(
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get specific email template"""
    template = next((t for t in _email_templates if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return EmailTemplate(**template)


@router.put("/email-templates/{template_id}", response_model=EmailTemplate)
@limiter.limit("10/minute")
async def update_email_template(
    request: Request,
    template_id: str,
    data: EmailTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update email template"""
    template = next((t for t in _email_templates if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    audit_old = template.copy()

    template["subject"] = data.subject
    template["body_html"] = data.body_html
    if data.body_text:
        template["body_text"] = data.body_text
    template["last_updated"] = datetime.now(timezone.utc)

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="email_template",
        entity_id=None,
        old_values=_serialize_for_audit(audit_old),
        new_values=_serialize_for_audit(template),
        changes_summary=f"Email template '{template_id}' updated",
    )

    return EmailTemplate(**template)


@router.get("/feature-flags", response_model=List[FeatureFlag])
async def get_feature_flags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Get all feature flags"""
    return [FeatureFlag(**f) for f in _feature_flags]


@router.put("/feature-flags/{flag_name}", response_model=dict)
@limiter.limit("10/minute")
async def update_feature_flag(
    request: Request,
    flag_name: str,
    enabled: bool = Body(...),
    rollout_percentage: int = Body(100, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Update feature flag status"""
    flag = next((f for f in _feature_flags if f["name"] == flag_name), None)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    audit_old = flag.copy()

    flag["enabled"] = enabled
    flag["rollout_percentage"] = rollout_percentage
    flag["updated_at"] = datetime.now(timezone.utc)

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="feature_flag",
        entity_id=None,
        old_values=_serialize_for_audit(audit_old),
        new_values=_serialize_for_audit(flag),
        changes_summary=f"Feature flag '{flag_name}' set to {enabled} ({rollout_percentage}%)",
    )

    return FeatureFlag(**flag)


@router.post("/maintenance-mode", response_model=dict)
@limiter.limit("5/minute")
async def toggle_maintenance_mode(
    request: Request,
    enabled: bool = Body(..., embed=True),
    message: str = Body("", max_length=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """Toggle maintenance mode - CRITICAL ACTION"""
    _system_settings["maintenance_mode"] = enabled

    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="maintenance_mode",
        old_values={"maintenance_mode": not enabled},
        new_values={"maintenance_mode": enabled, "message": message},
        changes_summary=f"Maintenance mode {'ENABLED' if enabled else 'DISABLED'} by super admin",
    )

    return {
        "maintenance_mode": enabled,
        "message": message or "Site under maintenance. Please check back soon.",
    }
