"""
Availability Service - Gestiona disponibilidad de habitaciones y tours
Previene overbookings verificando conflictos con reservas existentes
y entradas del calendario de disponibilidad.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Booking, BookingStatus
from app.models.room_availability import RoomAvailability


async def check_room_availability(
    db: AsyncSession,
    room_id: str,
    check_in: datetime,
    check_out: datetime,
    exclude_booking_id: Optional[str] = None,
) -> bool:
    """
    Check if a room is available for the given date range.

    A room is NOT available if:
    - There's a non-cancelled booking that overlaps with the requested range
    - There's a RoomAvailability entry marking a date as unavailable

    Args:
        db: Database session
        room_id: Room UUID
        check_in: Requested check-in date
        check_out: Requested check-out date
        exclude_booking_id: Optional booking ID to exclude (for rebooking scenarios)

    Returns:
        True if available, False if there's a conflict
    """
    # Check 1: Existing bookings
    query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            Booking.status.in_(
                [
                    BookingStatus.PENDING,
                    BookingStatus.CONFIRMED,
                    BookingStatus.COMPLETED,
                ]
            ),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
    )

    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)

    result = await db.execute(query)
    conflicting_bookings = result.scalars().all()

    if conflicting_bookings:
        return False

    # Check 2: RoomAvailability entries (vendor-blocked dates)
    # Generate the list of dates in the range
    current = check_in.date()
    end = check_out.date()
    dates_in_range = []
    while current < end:
        dates_in_range.append(current)
        current += timedelta(days=1)

    if dates_in_range:
        avail_result = await db.execute(
            select(RoomAvailability).where(
                and_(
                    RoomAvailability.room_id == room_id,
                    RoomAvailability.date.in_(dates_in_range),
                    RoomAvailability.is_available == False,
                )
            )
        )
        blocked_dates = avail_result.scalars().all()
        if blocked_dates:
            return False

    return True


async def get_room_availability_calendar(
    db: AsyncSession, room_id: str, start_date: datetime, end_date: datetime
) -> List[dict]:
    """
    Get availability calendar for a room in a date range.
    Returns a list of dates with availability status.
    Combines data from RoomAvailability table and existing bookings.
    """
    # Get all RoomAvailability entries for the range
    avail_result = await db.execute(
        select(RoomAvailability).where(
            and_(
                RoomAvailability.room_id == room_id,
                RoomAvailability.date >= start_date.date(),
                RoomAvailability.date < end_date.date(),
            )
        )
    )
    avail_entries = {a.date.isoformat(): a for a in avail_result.scalars().all()}

    # Get all bookings for this room in the date range
    query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.check_in < end_date,
            Booking.check_out > start_date,
        )
    )

    result = await db.execute(query)
    bookings = result.scalars().all()

    # Build availability map
    availability = []
    current = start_date
    while current < end_date:
        date_key = current.date().isoformat()
        is_today = current.date() == datetime.now(timezone.utc).date()
        is_past = current.date() < datetime.now(timezone.utc).date()

        # Check RoomAvailability entry
        avail_entry = avail_entries.get(date_key)

        # Check if booked
        is_booked = False
        for booking in bookings:
            if booking.check_in.date() <= current.date() < booking.check_out.date():
                is_booked = True
                break

        # Determine availability: prefer RoomAvailability if set, else check bookings
        if avail_entry is not None:
            is_available = avail_entry.is_available and not is_booked
            price_override = (
                float(avail_entry.price_override)
                if avail_entry.price_override
                else None
            )
            min_stay = avail_entry.min_stay
            max_stay = avail_entry.max_stay
        else:
            is_available = not is_booked and not is_past
            price_override = None
            min_stay = None
            max_stay = None

        day = {
            "date": date_key,
            "available": is_available,
            "is_today": is_today,
            "is_past": is_past,
        }
        if price_override is not None:
            day["price_override"] = price_override
        if min_stay is not None:
            day["min_stay"] = min_stay
        if max_stay is not None:
            day["max_stay"] = max_stay

        availability.append(day)
        current += timedelta(days=1)

    return availability


async def check_tour_availability(
    db: AsyncSession, tour_id: str, booking_date: datetime, participants: int
) -> tuple[bool, str]:
    """
    Check if a tour is available for the given date and participants.

    Returns:
        (is_available, reason)
    """
    from app.models.tour import Tour

    # Get tour details
    tour_result = await db.execute(select(Tour).where(Tour.id == tour_id))
    tour = tour_result.scalar_one_or_none()

    if not tour:
        return False, "Tour not found"

    if not tour.is_active:
        return False, "Tour is not active"

    # Check if tour runs on this day of week
    day_name = booking_date.strftime("%A").lower()
    if tour.schedule_days and day_name not in tour.schedule_days:
        return False, f"Tour not available on {day_name}"

    # Count existing bookings for this date
    query = select(Booking).where(
        and_(
            Booking.tour_id == tour_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            func.date(Booking.check_in) == booking_date.date(),
        )
    )

    result = await db.execute(query)
    existing_bookings = result.scalars().all()

    booked_participants = sum(b.participants for b in existing_bookings)
    available_spots = tour.max_group_size - booked_participants

    if participants > available_spots:
        return False, f"Only {available_spots} spots available for this date"

    return True, "Available"


async def get_next_available_dates(
    db: AsyncSession,
    room_id: str,
    nights: int,
    from_date: datetime,
    max_results: int = 5,
) -> List[dict]:
    """
    Find next available date ranges for a room.
    Useful for showing alternatives when dates are unavailable.
    """
    available_ranges = []
    current_start = from_date

    while len(available_ranges) < max_results:
        current_end = current_start + timedelta(days=nights)

        is_available = await check_room_availability(
            db, room_id, current_start, current_end
        )

        if is_available:
            available_ranges.append(
                {
                    "check_in": current_start.isoformat(),
                    "check_out": current_end.isoformat(),
                    "nights": nights,
                }
            )

        current_start += timedelta(days=1)

        # Stop after checking 90 days ahead
        if (current_start - from_date).days > 90:
            break

    return available_ranges
