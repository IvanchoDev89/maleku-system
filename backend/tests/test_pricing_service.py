"""
Tests for pricing service logic
"""

import pytest
from datetime import datetime
from app.services.pricing_service import (
    is_weekend,
    count_weekend_nights,
    calculate_room_price,
    calculate_tour_price,
    calculate_commission,
    apply_weekly_discount,
)


class MockRoom:
    """Mock room for testing"""

    def __init__(
        self,
        price_per_night=100,
        weekend_price=None,
        extra_guest_price=20,
        max_occupancy=2,
        currency="USD",
    ):
        self.price_per_night = price_per_night
        self.base_price = price_per_night
        self.weekend_price = weekend_price or price_per_night
        self.extra_guest_price = extra_guest_price
        self.max_guests = max_occupancy
        self.max_occupancy = max_occupancy
        self.currency = currency


class MockTour:
    """Mock tour for testing"""

    def __init__(self, price=50, currency="USD"):
        self.price = price
        self.currency = currency


def test_is_weekend():
    """Test weekend detection"""
    # Saturday (weekday 5)
    saturday = datetime(2024, 1, 6)
    assert is_weekend(saturday) is True

    # Sunday (weekday 6)
    sunday = datetime(2024, 1, 7)
    assert is_weekend(sunday) is True

    # Monday (weekday 0)
    monday = datetime(2024, 1, 8)
    assert is_weekend(monday) is False


def test_count_weekend_nights():
    """Test weekend night counting"""
    # Friday to Monday = 2 weekend nights (Friday and Saturday nights)
    check_in = datetime(2024, 1, 5)  # Friday
    check_out = datetime(2024, 1, 8)  # Monday

    weekend_nights = count_weekend_nights(check_in, check_out)
    assert weekend_nights == 2


def test_calculate_room_price_weekdays_only():
    """Test room price calculation for weekday stay"""
    room = MockRoom(price_per_night=100, weekend_price=150)

    # Monday to Wednesday (2 nights, both weekdays)
    check_in = datetime(2024, 1, 8)  # Monday
    check_out = datetime(2024, 1, 10)  # Wednesday

    pricing = calculate_room_price(room, check_in, check_out, guests=2)

    assert pricing["nights"] == 2
    assert pricing["weekday_nights"] == 2
    assert pricing["weekend_nights"] == 0
    assert pricing["subtotal"] == 200.0  # 2 nights * $100


def test_calculate_room_price_with_weekend():
    """Test room price calculation with weekend nights"""
    room = MockRoom(price_per_night=100, weekend_price=150)

    # Friday to Monday (3 nights: Friday, Saturday, Sunday nights)
    # But only Friday and Saturday nights count as "weekend nights" for pricing
    check_in = datetime(2024, 1, 5)  # Friday
    check_out = datetime(2024, 1, 8)  # Monday

    pricing = calculate_room_price(room, check_in, check_out, guests=2)

    assert pricing["nights"] == 3
    assert pricing["weekday_nights"] == 1  # Only the last night (to Monday)
    assert pricing["weekend_nights"] == 2  # Friday and Saturday nights
    # 1 weekday night * $100 + 2 weekend nights * $150 = $400
    assert pricing["subtotal"] == 400.0


def test_calculate_room_price_with_extra_guests():
    """Test room price with extra guest charges"""
    room = MockRoom(price_per_night=100, max_occupancy=2, extra_guest_price=25)

    check_in = datetime(2024, 1, 8)
    check_out = datetime(2024, 1, 10)

    # 4 guests, max occupancy 2 = 2 extra guests
    pricing = calculate_room_price(room, check_in, check_out, guests=4)

    assert pricing["extra_guests"] == 2
    assert pricing["extra_guests_total"] == 100.0  # 2 guests * $25 * 2 nights
    assert pricing["subtotal"] == 300.0  # $200 base + $100 extra


def test_calculate_room_price_single_night():
    """Test single night stay"""
    room = MockRoom(price_per_night=150)

    check_in = datetime(2024, 1, 8)
    check_out = datetime(2024, 1, 9)

    pricing = calculate_room_price(room, check_in, check_out, guests=1)

    assert pricing["nights"] == 1
    assert pricing["subtotal"] == 150.0


def test_calculate_room_price_less_than_one_night():
    """Test that less than one night raises error"""
    room = MockRoom(price_per_night=100)

    check_in = datetime(2024, 1, 8)
    check_out = datetime(2024, 1, 8)  # Same day

    with pytest.raises(ValueError, match="Minimum stay is 1 night"):
        calculate_room_price(room, check_in, check_out, guests=2)


def test_calculate_tour_price():
    """Test tour price calculation"""
    tour = MockTour(price=75, currency="USD")

    pricing = calculate_tour_price(tour, participants=3)

    assert pricing["participants"] == 3
    assert pricing["price_per_person"] == 75.0
    assert pricing["subtotal"] == 225.0  # 3 * $75
    assert pricing["currency"] == "USD"


def test_calculate_commission():
    """Test commission calculation"""
    # Default 10% commission
    assert calculate_commission(100.0) == 10.0
    assert calculate_commission(100.0, 0.10) == 10.0

    # Custom commission rate
    assert calculate_commission(100.0, 0.15) == 15.0
    assert calculate_commission(100.0, 0.05) == 5.0

    # Rounding
    assert calculate_commission(99.99) == 10.0


def test_apply_weekly_discount_no_discount():
    """Test weekly discount not applied for short stays"""
    subtotal = 600.0
    nights = 6

    result = apply_weekly_discount(subtotal, nights, discount_percentage=10.0)

    assert result == 600.0  # No discount applied


def test_apply_weekly_discount_applied():
    """Test weekly discount applied for 7+ night stays"""
    subtotal = 700.0
    nights = 7

    result = apply_weekly_discount(subtotal, nights, discount_percentage=10.0)

    assert result == 630.0  # $700 - 10% = $630


def test_apply_weekly_discount_no_percentage():
    """Test no discount when percentage is 0"""
    subtotal = 700.0
    nights = 7

    result = apply_weekly_discount(subtotal, nights, discount_percentage=0.0)

    assert result == 700.0  # No discount
