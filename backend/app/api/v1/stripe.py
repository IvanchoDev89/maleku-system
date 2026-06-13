"""
Stripe API - Checkout, webhooks y gestión de pagos
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import Optional
from urllib.parse import urlparse

from app.core.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models import User, Vendor, Booking, BookingStatus, ProcessedWebhook, Property
from app.services.stripe_service import (
    create_checkout_session,
    create_vendor_connect_account,
    get_connect_account_status,
    construct_webhook_event,
    handle_payment_success,
    handle_payment_failure,
    refund_payment,
    StripeError,
)
from app.services.email_service import email_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


def _validate_redirect_url(url: str) -> bool:
    """
    Valida que una URL de redirect pertenezca a nuestros dominios permitidos.
    Previene Open Redirect attacks.
    """
    try:
        parsed = urlparse(url)

        # Solo permitir http/https
        if parsed.scheme not in ("http", "https"):
            return False

        # Lista de hosts permitidos desde settings
        site_hostname = urlparse(settings.SITE_URL).hostname or "costaricatravel.dev"
        allowed_hosts = {
            site_hostname,
            f"www.{site_hostname}",
            f"app.{site_hostname}",
            "localhost",
            "127.0.0.1",
        }

        # Permitir localhost con cualquier puerto en desarrollo
        hostname = parsed.hostname
        if not hostname:
            return False

        # Check exact match o localhost con puerto
        if hostname in allowed_hosts:
            return True

        # Para localhost, permitir cualquier puerto
        if hostname == "localhost" or hostname.startswith("127.0.0."):
            return True

        return False

    except (ValueError, TypeError) as e:
        logger.warning(f"URL validation error in _validate_redirect_url: {e}")
        return False


class CheckoutRequest(BaseModel):
    booking_id: UUID
    success_url: str
    cancel_url: str

    @field_validator("success_url", "cancel_url")
    @classmethod
    def validate_redirect_urls(cls, v: str) -> str:
        """Validar que las URLs de redirect sean seguras."""
        if not _validate_redirect_url(v):
            raise ValueError(
                f"Invalid redirect URL: {v}. Must be a valid URL on our domain."
            )
        return v


class CheckoutResponse(BaseModel):
    session_id: str
    checkout_url: str


class VendorConnectResponse(BaseModel):
    account_id: Optional[str]
    onboarding_url: Optional[str]
    status: str


class WebhookResponse(BaseModel):
    status: str
    booking_id: Optional[str] = None
    payment_intent_id: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    event_id: Optional[str] = None


class StripeConfigResponse(BaseModel):
    publishable_key: str
    currency: str


class PaymentStatusResponse(BaseModel):
    booking_id: str
    confirmation_code: str
    status: str
    payment_intent_id: Optional[str] = None
    payment_status: Optional[str] = None
    total_amount: float
    currency: str


class RefundResponse(BaseModel):
    refund_id: str
    amount: float
    status: str
    booking_status: str


class RefundRequest(BaseModel):
    amount: Optional[float] = None  # If None, full refund
    reason: Optional[str] = None


async def update_booking_payment_status(
    db: AsyncSession, booking_id: str, payment_intent_id: str, status: str
):
    """Helper to update booking status from webhook"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if booking:
        booking.stripe_payment_intent_id = payment_intent_id
        booking.stripe_payment_status = status

        if status == "succeeded":
            booking.status = BookingStatus.CONFIRMED
        elif status == "failed":
            booking.status = BookingStatus.CANCELLED

        await db.flush()
        await db.commit()


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe Checkout Session for a booking.
    User is redirected to Stripe to complete payment.
    """
    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == data.booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    # Verify user owns this booking
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    # Check booking status
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking is {booking.status.value}, cannot create checkout",
        )

    # Get vendor
    vendor_result = await db.execute(
        select(Vendor).where(Vendor.id == booking.vendor_id)
    )
    vendor = vendor_result.scalar_one_or_none()

    try:
        session = await asyncio.to_thread(
            create_checkout_session,
            booking=booking,
            vendor=vendor,
            success_url=data.success_url,
            cancel_url=data.cancel_url,
            customer_email=current_user.email,
        )

        # Update booking with payment intent ID
        booking.stripe_payment_intent_id = session["payment_intent_id"]
        await db.flush()
        await db.commit()

        return CheckoutResponse(
            session_id=session["session_id"], checkout_url=session["url"]
        )

    except StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/vendor/connect", response_model=VendorConnectResponse)
async def get_vendor_connect_link(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Get or create Stripe Connect account for vendor.
    Returns onboarding URL for vendor to complete setup.
    """
    if current_user.role.value != "vendor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can connect Stripe accounts",
        )

    # Get vendor
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found"
        )

    # If already connected, check status
    if vendor.stripe_account_id:
        try:
            connect_status = get_connect_account_status(vendor.stripe_account_id)

            if connect_status["charges_enabled"] and connect_status["payouts_enabled"]:
                vendor.stripe_connected = True
                await db.flush()
                await db.commit()

                return VendorConnectResponse(
                    account_id=vendor.stripe_account_id,
                    onboarding_url=None,
                    status="connected",
                )
            else:
                # Need to complete onboarding
                return VendorConnectResponse(
                    account_id=vendor.stripe_account_id,
                    onboarding_url=None,
                    status="pending_verification",
                )

        except StripeError as e:
            logger.warning(f"Failed to get Stripe account status, will create new: {e}")
            pass  # Fall through to create new account

    # Create new Connect account
    try:
        base_url = settings.SITE_URL or "https://costaricatravel.dev"
        connect_data = create_vendor_connect_account(
            vendor=vendor,
            refresh_url=f"{base_url}/vendor/stripe/refresh",
            return_url=f"{base_url}/vendor/stripe/success",
        )

        # Save account ID
        vendor.stripe_account_id = connect_data["account_id"]
        await db.flush()
        await db.commit()

        return VendorConnectResponse(
            account_id=connect_data["account_id"],
            onboarding_url=connect_data["onboarding_url"],
            status="onboarding_required",
        )

    except StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/webhook", response_model=WebhookResponse)
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhooks for payment events.
    Updates booking status and sends confirmation emails.
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header",
        )

    # Get raw body
    payload = await request.body()

    try:
        # Verify and construct event
        event = await asyncio.to_thread(
            construct_webhook_event, payload, stripe_signature
        )
        event_id = event["id"]
        event_type = event["type"]

        # CRITICAL: Prevent replay attacks - check if already processed
        existing = await db.execute(
            select(ProcessedWebhook).where(ProcessedWebhook.event_id == event_id)
        )
        if existing.scalar_one_or_none():
            logger.warning(f"Webhook replay detected: {event_id} already processed")
            return JSONResponse({"status": "already_processed", "event_id": event_id})

        logger.info(f"Stripe webhook received: {event_type} ({event_id})")

        # Process event based on type
        response_data = {"status": "ignored"}

        if event_type == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            result = await asyncio.to_thread(handle_payment_success, payment_intent)

            booking_id = result.get("booking_id")
            if booking_id:
                await update_booking_payment_status(
                    db, booking_id, result["payment_intent_id"], "succeeded"
                )
                await _send_payment_confirmation_email(db, booking_id, result)
                logger.info(f"Payment succeeded for booking {booking_id}")

            response_data = {
                "status": "success",
                "booking_id": booking_id,
                "payment_intent_id": result["payment_intent_id"],
            }

        elif event_type == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            result = await asyncio.to_thread(handle_payment_failure, payment_intent)

            booking_id = result.get("booking_id")
            if booking_id:
                await update_booking_payment_status(
                    db, booking_id, result["payment_intent_id"], "failed"
                )
                logger.warning(f"Payment failed for booking {booking_id}")

            response_data = {
                "status": "failed",
                "booking_id": booking_id,
                "error": result["error_message"],
            }

        elif event_type == "charge.refunded":
            charge = event["data"]["object"]
            payment_intent_id = charge.get("payment_intent")

            if payment_intent_id:
                await _update_booking_refund_status(db, payment_intent_id)
                logger.info(f"Refund processed for payment {payment_intent_id}")

            response_data = {
                "status": "refund_processed",
                "payment_intent_id": payment_intent_id,
            }

        elif event_type == "checkout.session.completed":
            session = event["data"]["object"]
            booking_id = session.get("client_reference_id")
            payment_intent_id = session.get("payment_intent")

            if booking_id and payment_intent_id:
                await update_booking_payment_status(
                    db, booking_id, payment_intent_id, "succeeded"
                )
                logger.info(f"Checkout completed for booking {booking_id}")

            response_data = {
                "status": "checkout_completed",
                "session_id": session["id"],
                "booking_id": booking_id,
            }

        else:
            logger.debug(f"Unhandled Stripe event: {event_type}")

        # Mark webhook as processed to prevent replays
        processed = ProcessedWebhook(event_id=event_id, event_type=event_type)
        db.add(processed)
        await db.commit()
        logger.debug(f"Marked webhook {event_id} as processed")

        return JSONResponse(response_data)

    except StripeError as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.error(f"Webhook processing error: {e}")
        # Return 200 to prevent Stripe retries
        return JSONResponse({"status": "error", "message": str(e)}, status_code=200)


async def _send_payment_confirmation_email(
    db: AsyncSession, booking_id: str, payment_result: dict
):
    """Helper to send payment confirmation email"""
    try:
        result = await db.execute(
            select(Booking, User, Property)
            .join(User, Booking.user_id == User.id)
            .outerjoin(Property, Booking.property_id == Property.id)
            .where(Booking.id == booking_id)
        )
        row = result.first()

        if row:
            booking, user, property = row
            await email_service.send_payment_receipt(
                to=user.email,
                booking_code=booking.confirmation_code,
                payment_amount=payment_result["amount_received"],
                currency=payment_result["currency"].upper(),
            )
            logger.info(f"Payment confirmation email sent to {user.email}")
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error(f"Failed to send payment confirmation email: {e}")


async def _update_booking_refund_status(db: AsyncSession, payment_intent_id: str):
    """Helper to update booking status after refund"""
    try:
        result = await db.execute(
            select(Booking).where(Booking.stripe_payment_intent_id == payment_intent_id)
        )
        booking = result.scalar_one_or_none()

        if booking:
            booking.status = BookingStatus.REFUNDED
            booking.stripe_payment_status = "refunded"
            await db.flush()
            await db.commit()
            logger.info(f"Booking {booking.id} marked as refunded")
    except (OSError, RuntimeError, ValueError) as e:
        logger.error(f"Failed to update booking refund status: {e}")


@router.post("/bookings/{booking_id}/refund", response_model=RefundResponse)
async def refund_booking(
    booking_id: UUID,
    data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Refund a booking (full or partial).
    Only vendors and admins can process refunds.
    """
    # Check permissions
    if current_user.role.value not in ["vendor", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process refunds",
        )

    # Get booking
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    # Verify vendor owns this booking (if vendor)
    if current_user.role.value == "vendor":
        vendor_result = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = vendor_result.scalar_one_or_none()

        if not vendor or booking.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    # Check payment status
    if not booking.stripe_payment_intent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No payment to refund"
        )

    # Calculate refund amount
    refund_amount = data.amount if data.amount else booking.total_amount

    # Validate refund amount
    if refund_amount > booking.total_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund amount exceeds booking total",
        )

    try:
        result = await asyncio.to_thread(
            refund_payment,
            payment_intent_id=booking.stripe_payment_intent_id,
            amount=refund_amount if data.amount else None,
            reason=data.reason,
        )

        # Update booking status
        if refund_amount >= booking.total_amount:
            booking.status = BookingStatus.REFUNDED
        booking.stripe_payment_status = "refunded"

        await db.flush()
        await db.commit()

        return {
            "refund_id": result["refund_id"],
            "amount": result["amount"],
            "status": result["status"],
            "booking_status": booking.status.value,
        }

    except StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/config", response_model=StripeConfigResponse)
async def get_stripe_config():
    """
    Get public Stripe configuration for frontend.
    """
    return {
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "currency": "usd",
    }


@router.get(
    "/bookings/{booking_id}/payment-status", response_model=PaymentStatusResponse
)
async def check_payment_status(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Check payment status of a booking.
    Used by frontend to verify payment after redirect from Stripe.
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    # Verify user owns this booking or is vendor/admin
    if current_user.role.value == "client" and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    if current_user.role.value == "vendor":
        vendor_result = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = vendor_result.scalar_one_or_none()
        if not vendor or booking.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    return {
        "booking_id": str(booking.id),
        "confirmation_code": booking.confirmation_code,
        "status": booking.status.value,
        "payment_intent_id": booking.stripe_payment_intent_id,
        "payment_status": booking.stripe_payment_status,
        "total_amount": booking.total_amount,
        "currency": booking.currency,
    }
