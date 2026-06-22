"""
Pricing Service - Calcula precios reales de bookings con lógica de negocio
"""

from datetime import datetime, timedelta
from app.models import Room, Tour


def is_weekend(date: datetime) -> bool:
    """Check if date is weekend (Saturday=5, Sunday=6)"""
    return date.weekday() >= 5


def count_weekend_nights(check_in: datetime, check_out: datetime) -> int:
    """Count nights that fall on Friday or Saturday (weekend pricing)"""
    weekend_nights = 0
    current = check_in
    while current < check_out:
        # Friday night = Saturday morning (weekday 5)
        # Saturday night = Sunday morning (weekday 6)
        if current.weekday() in [5, 6]:  # Saturday or Sunday
            weekend_nights += 1
        current += timedelta(days=1)
    return weekend_nights


def calculate_room_price(
    room: Room,
    check_in: datetime,
    check_out: datetime,
    guests: int,
    include_taxes: bool = True,
) -> dict:
    """
    Calculate room booking price breakdown

    Returns dict with:
    - base_price: precio base de la habitación
    - weekend_nights: noches de fin de semana
    - weekday_nights: noches entre semana
    - extra_guests: huéspedes extra cobrados
    - extra_guest_price: precio por huésped extra
    - subtotal: antes de comisión
    - nights: total noches
    """
    nights = (check_out - check_in).days
    if nights < 1:
        raise ValueError("Minimum stay is 1 night")

    # Count weekend vs weekday nights
    weekend_nights = count_weekend_nights(check_in, check_out)
    weekday_nights = nights - weekend_nights

    # Calculate base price per night
    weekday_price = float(room.price_per_night or 0)
    weekend_price = float(room.weekend_price or weekday_price)

    # Calculate subtotal
    weekday_total = weekday_nights * weekday_price
    weekend_total = weekend_nights * weekend_price
    base_subtotal = weekday_total + weekend_total

    # Extra guests calculation
    max_guests = room.max_guests or 2
    extra_guests = max(0, guests - max_guests)
    extra_guest_price = float(room.extra_guest_price or 0)
    extra_guests_total = extra_guests * extra_guest_price * nights

    subtotal = base_subtotal + extra_guests_total

    return {
        "nights": nights,
        "weekday_nights": weekday_nights,
        "weekend_nights": weekend_nights,
        "weekday_price": weekday_price,
        "weekend_price": weekend_price,
        "weekday_total": weekday_total,
        "weekend_total": weekend_total,
        "base_subtotal": base_subtotal,
        "guests": guests,
        "max_occupancy": max_guests,
        "extra_guests": extra_guests,
        "extra_guest_price": extra_guest_price,
        "extra_guests_total": extra_guests_total,
        "subtotal": subtotal,
        "currency": "USD",
    }


def calculate_tour_price(tour: Tour, participants: int) -> dict:
    """
    Calculate tour booking price breakdown
    """
    price_per_person = float(tour.price or 0)
    subtotal = price_per_person * participants

    return {
        "participants": participants,
        "price_per_person": price_per_person,
        "subtotal": subtotal,
        "currency": tour.currency or "USD",
    }


def calculate_commission_amount(amount: float, commission_rate: float = 0.10) -> float:
    """Calculate platform commission amount only"""
    return round(amount * commission_rate, 2)


def calculate_commission_breakdown(
    amount: float, commission_rate: float = 0.10
) -> dict:
    """
    Calculate platform commission with full breakdown.

    Returns dict with:
    - amount: original amount
    - commission_rate: rate used
    - commission: commission amount
    - vendor_amount: amount after commission
    """
    commission = round(amount * commission_rate, 2)
    vendor_amount = round(amount - commission, 2)

    return {
        "amount": amount,
        "commission_rate": commission_rate,
        "commission": commission,
        "vendor_amount": vendor_amount,
    }


def apply_weekly_discount(
    subtotal: float, nights: int, discount_percentage: float = 0.0
) -> float:
    """Apply weekly discount if stay is 7+ nights"""
    if nights >= 7 and discount_percentage > 0:
        discount = subtotal * (discount_percentage / 100)
        return round(subtotal - discount, 2)
    return subtotal


# Backward compatibility alias
calculate_commission = calculate_commission_amount
