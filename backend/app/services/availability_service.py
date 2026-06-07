"""
Availability Service - Gestiona disponibilidad de habitaciones y tours
Previene overbookings verificando conflictos con reservas existentes
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Booking, BookingStatus, Tour


async def check_room_availability(
    db: AsyncSession,
    room_id: str,
    check_in: datetime,
    check_out: datetime,
    exclude_booking_id: Optional[str] = None
) -> bool:
    """
    Check if a room is available for the given date range.
    
    A room is NOT available if there's an existing booking that:
    - Is not cancelled/refunded
    - Overlaps with the requested date range
    
    Args:
        db: Database session
        room_id: Room UUID
        check_in: Requested check-in date
        check_out: Requested check-out date
        exclude_booking_id: Optional booking ID to exclude (for rebooking scenarios)
    
    Returns:
        True if available, False if there's a conflict
    """
    query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
            or_(
                # Case 1: Existing booking starts during our stay
                and_(
                    Booking.check_in >= check_in,
                    Booking.check_in < check_out
                ),
                # Case 2: Existing booking ends during our stay
                and_(
                    Booking.check_out > check_in,
                    Booking.check_out <= check_out
                ),
                # Case 3: Existing booking completely covers our stay
                and_(
                    Booking.check_in <= check_in,
                    Booking.check_out >= check_out
                ),
                # Case 4: Our stay completely covers existing booking
                and_(
                    Booking.check_in >= check_in,
                    Booking.check_out <= check_out
                )
            )
        )
    )
    
    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)
    
    result = await db.execute(query)
    conflicting_bookings = result.scalars().all()
    
    return len(conflicting_bookings) == 0


async def get_room_availability_calendar(
    db: AsyncSession,
    room_id: str,
    start_date: datetime,
    end_date: datetime
) -> List[dict]:
    """
    Get availability calendar for a room in a date range.
    Returns a list of dates with availability status.
    """
    # Get all bookings for this room in the date range
    query = select(Booking).where(
        and_(
            Booking.room_id == room_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.check_in < end_date,
            Booking.check_out > start_date
        )
    )
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    # Build availability map
    availability = []
    current = start_date
    while current < end_date:
        is_available = True
        for booking in bookings:
            if booking.check_in <= current < booking.check_out:
                is_available = False
                break
        
        availability.append({
            "date": current.isoformat(),
            "available": is_available
        })
        current += timedelta(days=1)
    
    return availability


async def check_tour_availability(
    db: AsyncSession,
    tour_id: str,
    booking_date: datetime,
    participants: int
) -> tuple[bool, str]:
    """
    Check if a tour is available for the given date and participants.
    
    Returns:
        (is_available, reason)
    """
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
            func.date(Booking.check_in) == booking_date.date()
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
    max_results: int = 5
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
            available_ranges.append({
                "check_in": current_start.isoformat(),
                "check_out": current_end.isoformat(),
                "nights": nights
            })
        
        current_start += timedelta(days=1)
        
        # Stop after checking 90 days ahead
        if (current_start - from_date).days > 90:
            break
    
    return available_ranges
