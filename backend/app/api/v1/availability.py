"""
Availability API - Endpoints para consultar disponibilidad de habitaciones y tours
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.services.availability_service import (
    check_room_availability,
    get_room_availability_calendar,
    check_tour_availability,
    get_next_available_dates
)

router = APIRouter()


class AvailabilityCheckRequest(BaseModel):
    room_id: UUID
    check_in: datetime
    check_out: datetime


class AvailabilityCheckResponse(BaseModel):
    available: bool
    alternative_dates: list = []


class AvailabilityCalendarResponse(BaseModel):
    room_id: UUID
    dates: list


@router.post("/rooms/check", response_model=AvailabilityCheckResponse)
async def check_availability(
    data: AvailabilityCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a room is available for specific dates.
    If not available, returns alternative date suggestions.
    """
    is_available = await check_room_availability(
        db=db,
        room_id=str(data.room_id),
        check_in=data.check_in,
        check_out=data.check_out
    )
    
    alternative_dates = []
    if not is_available:
        # Suggest next available dates
        nights = (data.check_out - data.check_in).days
        alternative_dates = await get_next_available_dates(
            db=db,
            room_id=str(data.room_id),
            nights=nights,
            from_date=data.check_in,
            max_results=3
        )
    
    return AvailabilityCheckResponse(
        available=is_available,
        alternative_dates=alternative_dates
    )


@router.get("/rooms/{room_id}/calendar", response_model=AvailabilityCalendarResponse)
async def get_room_calendar(
    room_id: UUID,
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    days: int = Query(30, ge=1, le=90, description="Number of days to check"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get availability calendar for a room.
    Returns daily availability status for the requested period.
    """
    end_date = start_date + timedelta(days=days)
    
    calendar = await get_room_availability_calendar(
        db=db,
        room_id=str(room_id),
        start_date=start_date,
        end_date=end_date
    )
    
    return AvailabilityCalendarResponse(
        room_id=room_id,
        dates=calendar
    )


@router.post("/tours/check")
async def check_tour_availability_endpoint(
    tour_id: UUID,
    booking_date: datetime,
    participants: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a tour is available for a specific date and number of participants.
    """
    is_available, reason = await check_tour_availability(
        db=db,
        tour_id=str(tour_id),
        booking_date=booking_date,
        participants=participants
    )
    
    return {
        "available": is_available,
        "message": reason if not is_available else "Available",
        "tour_id": tour_id,
        "date": booking_date.isoformat(),
        "participants": participants
    }


@router.get("/rooms/{room_id}/next-available")
async def get_next_available(
    room_id: UUID,
    nights: int = Query(1, ge=1, description="Number of nights needed"),
    from_date: Optional[datetime] = None,
    max_results: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Get next available date ranges for a room.
    Useful for showing alternatives when requested dates are unavailable.
    """
    if from_date is None:
        from_date = datetime.now(timezone.utc)
    
    available_ranges = await get_next_available_dates(
        db=db,
        room_id=str(room_id),
        nights=nights,
        from_date=from_date,
        max_results=max_results
    )
    
    return {
        "room_id": room_id,
        "nights": nights,
        "available_ranges": available_ranges
    }
