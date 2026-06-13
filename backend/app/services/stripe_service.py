"""
Stripe Service - Gestiona pagos, checkout sessions y webhooks
Integración completa con Stripe Connect para marketplace multi-vendor
"""

import stripe
from typing import Optional, Dict, Any
from app.core.config import settings
from app.models import Booking, Vendor

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = "2023-10-16"

# Constants
CENTS_PER_DOLLAR = 100
DEFAULT_COUNTRY_CODE = "CR"  # Costa Rica
DEFAULT_CURRENCY = "usd"


class StripeError(Exception):
    """Custom Stripe error"""

    pass


def create_checkout_session(
    booking: Booking,
    vendor: Vendor,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a Stripe Checkout Session for a booking.

    For marketplace with Stripe Connect:
    - Platform collects full amount
    - Vendor receives amount minus commission
    - Commission goes to platform account
    """
    try:
        # Build line items
        if booking.booking_type == "property":
            line_items = [
                {
                    "price_data": {
                        "currency": booking.currency.lower(),
                        "product_data": {
                            "name": f"Booking #{booking.confirmation_code}",
                            "description": f"Stay from {booking.check_in.date()} to {booking.check_out.date()}",
                        },
                        "unit_amount": int(
                            booking.total_amount * CENTS_PER_DOLLAR
                        ),  # cents
                    },
                    "quantity": 1,
                }
            ]
        else:  # tour
            line_items = [
                {
                    "price_data": {
                        "currency": booking.currency.lower(),
                        "product_data": {
                            "name": f"Tour Booking #{booking.confirmation_code}",
                            "description": f"Tour on {booking.check_in.date()}",
                        },
                        "unit_amount": int(
                            booking.total_amount * CENTS_PER_DOLLAR
                        ),  # cents
                    },
                    "quantity": 1,
                }
            ]

        # Calculate amounts for Connect
        vendor_amount = int(
            (booking.total_amount - booking.commission_amount) * CENTS_PER_DOLLAR
        )
        platform_amount = int(booking.commission_amount * CENTS_PER_DOLLAR)

        session_data = {
            "payment_method_types": ["card"],
            "line_items": line_items,
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(booking.id),
            "metadata": {
                "booking_id": str(booking.id),
                "booking_type": booking.booking_type,
                "confirmation_code": booking.confirmation_code,
                "vendor_id": str(booking.vendor_id) if booking.vendor_id else None,
            },
        }

        # Add customer email if provided
        if customer_email:
            session_data["customer_email"] = customer_email

        # Stripe Connect: Transfer to vendor if connected
        if vendor and vendor.stripe_account_id and vendor.stripe_connected:
            session_data["payment_intent_data"] = {
                "transfer_group": str(booking.id),
                "application_fee_amount": platform_amount,
                "transfer_data": {
                    "destination": vendor.stripe_account_id,
                    "amount": vendor_amount,
                },
            }
        else:
            # No Connect account, platform keeps all and pays vendor manually
            session_data["payment_intent_data"] = {
                "metadata": {
                    "manual_payout": "true",
                    "vendor_amount": str(vendor_amount),
                    "platform_amount": str(platform_amount),
                }
            }

        session = stripe.checkout.Session.create(**session_data)

        return {
            "session_id": session.id,
            "url": session.url,
            "payment_intent_id": session.payment_intent,
        }

    except stripe.error.StripeError as e:
        raise StripeError(f"Stripe error: {str(e)}") from e


def create_vendor_connect_account(
    vendor: Vendor, refresh_url: str, return_url: str
) -> Dict[str, Any]:
    """
    Create a Stripe Connect Express account for a vendor.
    Returns onboarding link.
    """
    try:
        # Create Connect account
        account = stripe.Account.create(
            type="express",
            country=DEFAULT_COUNTRY_CODE,  # Costa Rica
            email=vendor.email,
            business_type="individual",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            metadata={
                "vendor_id": str(vendor.id),
                "business_name": vendor.business_name,
            },
        )

        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=refresh_url,
            return_url=return_url,
            type="account_onboarding",
        )

        return {
            "account_id": account.id,
            "onboarding_url": account_link.url,
        }

    except stripe.error.StripeError as e:
        raise StripeError(f"Stripe error: {str(e)}")


def get_connect_account_status(account_id: str) -> Dict[str, Any]:
    """Get Stripe Connect account status"""
    try:
        account = stripe.Account.retrieve(account_id)
        return {
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
            "requirements": account.requirements,
        }
    except stripe.error.StripeError as e:
        raise StripeError(f"Stripe error: {str(e)}")


def construct_webhook_event(payload: bytes, sig_header: str) -> Any:
    """
    Construct and verify Stripe webhook event.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise StripeError("Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError as e:
        raise StripeError(f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        raise StripeError(f"Invalid signature: {str(e)}")


def handle_payment_success(payment_intent: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process successful payment webhook.
    Returns booking_id and amount for confirmation.
    """
    metadata = payment_intent.get("metadata", {})
    booking_id = metadata.get("booking_id")

    if not booking_id:
        raise StripeError("No booking_id in payment intent metadata")

    return {
        "booking_id": booking_id,
        "payment_intent_id": payment_intent["id"],
        "amount_received": payment_intent["amount_received"]
        / CENTS_PER_DOLLAR,  # Convert from cents
        "currency": payment_intent["currency"],
        "status": payment_intent["status"],
    }


def handle_payment_failure(payment_intent: Dict[str, Any]) -> Dict[str, Any]:
    """Process failed payment webhook"""
    metadata = payment_intent.get("metadata", {})
    booking_id = metadata.get("booking_id")

    return {
        "booking_id": booking_id,
        "payment_intent_id": payment_intent["id"],
        "status": "failed",
        "error_message": payment_intent.get("last_payment_error", {}).get(
            "message", "Unknown error"
        ),
    }


def refund_payment(
    payment_intent_id: str, amount: Optional[float] = None, reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Refund a payment (partial or full).
    """
    try:
        refund_data = {
            "payment_intent": payment_intent_id,
            "reason": "requested_by_customer" if reason else None,
        }

        if amount:
            refund_data["amount"] = int(amount * CENTS_PER_DOLLAR)  # Convert to cents

        refund = stripe.Refund.create(**refund_data)

        return {
            "refund_id": refund.id,
            "amount": refund.amount / CENTS_PER_DOLLAR,
            "status": refund.status,
        }

    except stripe.error.StripeError as e:
        raise StripeError(f"Refund error: {str(e)}")


def create_payout_to_vendor(
    vendor_account_id: str, amount: float, currency: str = DEFAULT_CURRENCY
) -> Dict[str, Any]:
    """
    Create manual payout to vendor (for vendors without Connect).
    This transfers from platform balance to vendor's external account.
    """
    try:
        transfer = stripe.Transfer.create(
            amount=int(amount * CENTS_PER_DOLLAR),
            currency=currency,
            destination=vendor_account_id,
        )

        return {
            "transfer_id": transfer.id,
            "amount": transfer.amount / CENTS_PER_DOLLAR,
            "status": transfer.status,
        }

    except stripe.error.StripeError as e:
        raise StripeError(f"Transfer error: {str(e)}")
