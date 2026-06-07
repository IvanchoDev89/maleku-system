"""
Newsletter API endpoints for email subscriptions.
"""
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.models import NewsletterSubscriber
from app.schemas import NewsletterSubscribe, NewsletterSubscribeResponse

router = APIRouter()
logger = get_logger(__name__)

# SECURITY: per-IP rate limit for the public subscribe endpoint
# Prevents email-bombing / DB-flooding from a single source.
_NEWSLETTER_LIMIT_PER_HOUR = 5
_newsletter_attempts: Dict[str, Deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def _enforce_newsletter_rate_limit(request: Request) -> None:
    """Allow at most N subscribe attempts per hour per IP."""
    ip = _client_ip(request)
    now = time.time()
    window_start = now - 3600
    attempts = _newsletter_attempts[ip]
    while attempts and attempts[0] < window_start:
        attempts.popleft()
    if len(attempts) >= _NEWSLETTER_LIMIT_PER_HOUR:
        logger.warning(f"Newsletter subscribe rate limit hit for IP {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many subscribe attempts. Please try again later.",
        )
    attempts.append(now)


@router.post("/subscribe", response_model=NewsletterSubscribeResponse)
async def subscribe_to_newsletter(
    request: Request,
    data: NewsletterSubscribe,
    db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to newsletter.

    - Checks if email already exists
    - Creates new subscriber if not exists
    - Reactivates if previously unsubscribed
    - Returns success message
    """
    # SECURITY: rate-limit per IP to prevent email-bombing
    _enforce_newsletter_rate_limit(request)

    # Check if email already exists
    query = select(NewsletterSubscriber).where(NewsletterSubscriber.email == data.email)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        if existing.is_active:
            # Already subscribed and active
            return NewsletterSubscribeResponse(
                success=True,
                message="Ya estás suscrito a nuestro newsletter."
            )
        else:
            # Reactivate subscription
            existing.is_active = True
            existing.unsubscribed_at = None
            await db.commit()
            return NewsletterSubscribeResponse(
                success=True,
                message="Tu suscripción ha sido reactivada. ¡Bienvenido de vuelta!"
            )

    # Create new subscriber
    confirmation_token = secrets.token_urlsafe(32)
    subscriber = NewsletterSubscriber(
        email=data.email,
        first_name=data.first_name,
        is_active=True,
        is_confirmed=False,
        source="landing_page",
        confirmation_token=confirmation_token
    )

    db.add(subscriber)
    await db.commit()

    # TODO: Send confirmation email

    return NewsletterSubscribeResponse(
        success=True,
        message="¡Gracias por suscribirte! Revisa tu correo para confirmar tu suscripción."
    )


@router.post("/unsubscribe", response_model=NewsletterSubscribeResponse)
async def unsubscribe_from_newsletter(
    email: str,
    db: AsyncSession = Depends(get_db)
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
        success=True,
        message="Has sido dado de baja del newsletter."
    )
