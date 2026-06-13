"""
Flights API - Vuelos
"""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.core.utils import escape_like_pattern
from app.models import UserRole, Flight, RouteType
from app.schemas import flight as flight_schema

router = APIRouter()



@router.get("", response_model=list[flight_schema.FlightResponse])
async def list_flights(
    origin_airport: str | None = None,
    destination_airport: str | None = None,
    route_type: RouteType | None = None,
    db: AsyncSession = Depends(get_db)
) -> list[flight_schema.FlightResponse]:
    """
    List all available flights with optional filters.

    Args:
        origin_airport: Filter by origin airport (IATA code or partial)
        destination_airport: Filter by destination airport (IATA code or partial)
        route_type: Filter by route type (international/domestic)
        db: Database session

    Returns:
        List of flights matching the filters
    """
    query = select(Flight).where(Flight.is_active, Flight.deleted_at.is_(None))

    if origin_airport:
        safe_origin = escape_like_pattern(origin_airport)
        query = query.where(Flight.origin_airport.ilike(f"%{safe_origin}%"))
    if destination_airport:
        safe_destination = escape_like_pattern(destination_airport)
        query = query.where(Flight.destination_airport.ilike(f"%{safe_destination}%"))
    if route_type:
        query = query.where(Flight.route_type == route_type)

    result = await db.execute(query.order_by(Flight.departure_time))
    flights = result.scalars().all()

    return flights


@router.get("/search", response_model=dict)
async def search_flights(
    origin: str,
    destination: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Search flights between two airports.

    Args:
        origin: Origin airport code (e.g., 'SJO', 'LAX')
        destination: Destination airport code
        db: Database session

    Returns:
        List of available flights between the specified airports
    """
    # Escape LIKE patterns for security
    safe_origin = escape_like_pattern(origin)
    safe_destination = escape_like_pattern(destination)

    result = await db.execute(
        select(Flight).where(
            Flight.is_active,
            Flight.deleted_at.is_(None),
            or_(
                Flight.origin_airport.ilike(f"%{safe_origin}%"),
                Flight.origin_airport == origin.upper()
            ),
            or_(
                Flight.destination_airport.ilike(f"%{safe_destination}%"),
                Flight.destination_airport == destination.upper()
            )
        ).order_by(Flight.price_economy)
    )
    flights = result.scalars().all()

    return {"flights": flights, "count": len(flights)}


@router.get("/{flight_id}", response_model=flight_schema.FlightDetailResponse)
async def get_flight(flight_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get flight details"""
    result = await db.execute(
        select(Flight).where(Flight.id == flight_id, Flight.deleted_at.is_(None))
    )
    flight = result.scalar_one_or_none()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    return flight


@router.post("", response_model=flight_schema.FlightResponse)
    flight_data: flight_schema.FlightCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Create new flight (Admin only)"""
    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'airline', 'flight_number', 'route_type', 'origin_airport',
                     'destination_airport', 'departure_time', 'arrival_time',
                     'duration_minutes', 'aircraft_type',
                     'price_economy', 'price_business', 'price_first',
                     'currency', 'baggage_allowance', 'amenities', 'schedule_days'}
    flight_data_filtered = {k: v for k, v in flight_data.model_dump().items() if k in allowed_fields}

    flight = Flight(**flight_data_filtered)

    db.add(flight)
    await db.commit()
    await db.refresh(flight)

    return flight


@router.put("/{flight_id}", response_model=flight_schema.FlightResponse)
async def update_flight(
    flight_id: uuid.UUID,
    flight_data: flight_schema.FlightUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    """Update flight (Admin only)"""
    result = await db.execute(
        select(Flight).where(Flight.id == flight_id, Flight.deleted_at.is_(None))
    )
    flight = result.scalar_one_or_none()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {'airline', 'flight_number', 'route_type', 'origin_airport',
                     'destination_airport', 'departure_time', 'arrival_time',
                     'duration_minutes', 'aircraft_type',
                     'price_economy', 'price_business', 'price_first',
                     'currency', 'baggage_allowance', 'amenities', 'schedule_days',
                     'is_active'}

    for key, value in flight_data.model_dump(exclude_unset=True).items():
        if key in allowed_fields:
            setattr(flight, key, value)

    flight.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(flight)

    return flight


@router.delete("/{flight_id}", response_model=dict)
async def delete_flight(
    flight_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(require_role(UserRole.ADMIN))
):
    """Soft-delete flight (Admin only)"""
    result = await db.execute(
        select(Flight).where(Flight.id == flight_id, Flight.deleted_at.is_(None))
    )
    flight = result.scalar_one_or_none()

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    flight.is_active = False
    flight.deleted_at = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Flight deleted"}
