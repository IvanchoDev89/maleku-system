"""
Newsletter API endpoints for email subscriptions.
"""

import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limiter import limiter
from app.models import NewsletterSubscriber
from app.schemas import NewsletterSubscribe, NewsletterSubscribeResponse
from app.services.email_service import email_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
@limiter.limit("5/hour")
async def subscribe_to_newsletter(
    request: Request, data: NewsletterSubscribe, db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to newsletter.

    - Checks if email already exists
    - Creates new subscriber if not exists
    - Reactivates if previously unsubscribed
    - Returns success message
    """

    # Check if email already exists
    query = select(NewsletterSubscriber).where(NewsletterSubscriber.email == data.email)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        if existing.is_active:
            # Already subscribed and active
            return NewsletterSubscribeResponse(
                success=True, message="Ya estás suscrito a nuestro newsletter."
            )
        else:
            # Reactivate subscription
            existing.is_active = True
            existing.unsubscribed_at = None
            await db.commit()
            return NewsletterSubscribeResponse(
                success=True,
                message="Tu suscripción ha sido reactivada. ¡Bienvenido de vuelta!",
            )

    # Create new subscriber
    confirmation_token = secrets.token_urlsafe(32)
    subscriber = NewsletterSubscriber(
        email=data.email,
        first_name=data.first_name,
        is_active=True,
        is_confirmed=False,
        source="landing_page",
        confirmation_token=confirmation_token,
    )

    db.add(subscriber)
    await db.commit()

    # Send confirmation email (MailHog in dev, Resend in prod)
    try:
        site_url = settings.SITE_URL
        confirm_link = f"{site_url}/newsletter/confirm?token={confirmation_token}"
        content = f"""
            <p>Thanks for subscribing to Costa Rica Travel!</p>
            <p>Please confirm your subscription by clicking the link below:</p>
            <p><a href="{confirm_link}"
                  style="background:#1e7a67;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">
                  Confirm Subscription
               </a></p>
            <p>If you didn't request this, you can ignore this email.</p>
        """
        await email_service.send_email(
            to=subscriber.email,
            subject="Confirm your Costa Rica Travel subscription",
            html=email_service._build_email_template("Confirm Subscription", content),
        )
    except Exception as e:  # noqa: BLE001
        logger.error(f"Failed to send newsletter confirmation: {e}")

    return NewsletterSubscribeResponse(
        success=True,
        message="¡Gracias por suscribirte! Revisa tu correo para confirmar tu suscripción.",
    )


@router.post("/unsubscribe", response_model=NewsletterSubscribeResponse)
@limiter.limit("5/hour")
async def unsubscribe_from_newsletter(
    request: Request, email: str, db: AsyncSession = Depends(get_db)
):
    """
    Unsubscribe from newsletter.

    Security: Returns same success message regardless of email existence
    to prevent email enumeration attacks.
    """
    query = select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
    result = await db.execute(query)
    subscriber = result.scalar_one_or_none()

    # Security: Always return success, even if email doesn't exist
    # This prevents email enumeration attacks
    if subscriber and subscriber.is_active:
        subscriber.is_active = False
        subscriber.unsubscribed_at = datetime.now(timezone.utc)
        await db.commit()

    # Always return generic success message
    return NewsletterSubscribeResponse(
        success=True, message="Has sido dado de baja del newsletter."
    )
