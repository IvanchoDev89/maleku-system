"""
Availability API - Endpoints para consultar y gestionar disponibilidad de habitaciones y tours
"""

from datetime import UTC, datetime, timedelta
from datetime import date as date_type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_permission
from app.models import Room, User, UserRole, Vendor
from app.models.room_availability import RoomAvailability
from app.services.availability_service import (
    check_room_availability,
    check_tour_availability,
    get_next_available_dates,
    get_room_availability_calendar,
)

router = APIRouter(tags=["Availability"])


# ============ READ MODELS ============


class AvailabilityCheckRequest(BaseModel):
    room_id: UUID
    check_in: datetime
    check_out: datetime


class AvailabilityCheckResponse(BaseModel):
    available: bool
    alternative_dates: list = []


class CalendarDay(BaseModel):
    date: str
    available: bool
    price_override: float | None = None
    min_stay: int | None = None
    max_stay: int | None = None


class AvailabilityCalendarResponse(BaseModel):
    room_id: UUID
    dates: list


# ============ WRITE MODELS ============


class CalendarEntry(BaseModel):
    date: date_type
    is_available: bool = True
    price_override: float | None = None
    min_stay: int | None = None
    max_stay: int | None = None
    notes: str | None = None


class BulkCalendarUpdate(BaseModel):
    entries: list[CalendarEntry]


class BulkCalendarResponse(BaseModel):
    room_id: UUID
    updated_count: int
    message: str


# ============ PUBLIC ENDPOINTS ============


@router.post("/rooms/check", response_model=AvailabilityCheckResponse)
@limiter.limit("30/minute")
async def check_availability(
    data: AvailabilityCheckRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Check if a room is available for specific dates.
    If not available, returns alternative date suggestions.
    """
    is_available = await check_room_availability(
        db=db,
        room_id=str(data.room_id),
        check_in=data.check_in,
        check_out=data.check_out,
    )

    alternative_dates = []
    if not is_available:
        nights = (data.check_out - data.check_in).days
        alternative_dates = await get_next_available_dates(
            db=db,
            room_id=str(data.room_id),
            nights=nights,
            from_date=data.check_in,
            max_results=3,
        )

    return AvailabilityCheckResponse(available=is_available, alternative_dates=alternative_dates)


@router.get("/rooms/{room_id}/calendar", response_model=AvailabilityCalendarResponse)
async def get_room_calendar(
    room_id: UUID,
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    days: int = Query(30, ge=1, le=365, description="Number of days to check"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get availability calendar for a room.
    Returns daily availability status for the requested period.
    Combines data from RoomAvailability table + existing bookings.
    """
    end_date = start_date + timedelta(days=days)

    calendar = await get_room_availability_calendar(
        db=db, room_id=str(room_id), start_date=start_date, end_date=end_date
    )

    return AvailabilityCalendarResponse(room_id=room_id, dates=calendar)


@router.post("/tours/check", response_model=dict)
@limiter.limit("30/minute")
async def check_tour_availability_endpoint(
    tour_id: UUID,
    booking_date: datetime,
    request: Request,
    participants: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
):
    """
    Check if a tour is available for a specific date and number of participants.
    """
    is_available, reason = await check_tour_availability(
        db=db,
        tour_id=str(tour_id),
        booking_date=booking_date,
        participants=participants,
    )

    return {
        "available": is_available,
        "message": reason if not is_available else "Available",
        "tour_id": tour_id,
        "date": booking_date.isoformat(),
        "participants": participants,
    }


@router.get("/rooms/{room_id}/next-available", response_model=dict)
async def get_next_available(
    room_id: UUID,
    nights: int = Query(1, ge=1, description="Number of nights needed"),
    from_date: datetime | None = None,
    max_results: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
):
    """
    Get next available date ranges for a room.
    Useful for showing alternatives when requested dates are unavailable.
    """
    if from_date is None:
        from_date = datetime.now(UTC)

    available_ranges = await get_next_available_dates(
        db=db,
        room_id=str(room_id),
        nights=nights,
        from_date=from_date,
        max_results=max_results,
    )

    return {"room_id": room_id, "nights": nights, "available_ranges": available_ranges}


# ============ MANAGEMENT ENDPOINTS (vendor/superadmin) ============


@router.put(
    "/rooms/{room_id}/calendar",
    response_model=BulkCalendarResponse,
    summary="Bulk update room calendar",
    description="Upsert availability entries for a room. Replaces existing entries for the specified dates. Vendor must own the room's property or be superadmin.",
)
@limiter.limit("10/minute")
async def bulk_update_calendar(
    request: Request,
    room_id: UUID,
    data: BulkCalendarUpdate,
    current_user: User = Depends(require_permission("properties", "update")),
    db: AsyncSession = Depends(get_db),
):
    # Verify room exists and ownership
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if current_user.role == UserRole.VENDOR:
        from app.models import Property

        prop_result = await db.execute(select(Property).where(Property.id == room.property_id))
        prop = prop_result.scalar_one_or_none()
        vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
        vendor = vendor_result.scalar_one_or_none()
        if not vendor or not prop or prop.vendor_id != vendor.id:
            raise HTTPException(
                status_code=403, detail="Not authorized to modify this room's calendar"
            )

    # Delete existing entries for these dates, then insert new ones
    dates = [e.date for e in data.entries]
    if dates:
        await db.execute(
            delete(RoomAvailability).where(
                RoomAvailability.room_id == room_id,
                RoomAvailability.date.in_(dates),
            )
        )

    for entry in data.entries:
        ra = RoomAvailability(
            room_id=room_id,
            date=entry.date,
            is_available=entry.is_available,
            price_override=entry.price_override,
            min_stay=entry.min_stay,
            max_stay=entry.max_stay,
            notes=entry.notes,
        )
        db.add(ra)

    await db.commit()

    return BulkCalendarResponse(
        room_id=room_id,
        updated_count=len(data.entries),
        message=f"Calendar updated for {len(data.entries)} date(s)",
    )


@router.delete(
    "/rooms/{room_id}/calendar/{date_str}",
    response_model=dict,
    summary="Delete a calendar entry",
    description="Remove a specific date's availability entry from the calendar. Vendor must own the room's property or be superadmin.",
)
async def delete_calendar_entry(
    room_id: UUID,
    date_str: str,
    current_user: User = Depends(require_permission("properties", "update")),
    db: AsyncSession = Depends(get_db),
):
    # Verify room exists and ownership (same check as above)
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if current_user.role == UserRole.VENDOR:
        from app.models import Property

        prop_result = await db.execute(select(Property).where(Property.id == room.property_id))
        prop = prop_result.scalar_one_or_none()
        vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
        vendor = vendor_result.scalar_one_or_none()
        if not vendor or not prop or prop.vendor_id != vendor.id:
            raise HTTPException(status_code=403, detail="Not authorized")

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    await db.execute(
        delete(RoomAvailability).where(
            RoomAvailability.room_id == room_id,
            RoomAvailability.date == target_date,
        )
    )
    await db.commit()

    return {
        "message": f"Calendar entry for {date_str} deleted",
        "room_id": str(room_id),
    }
