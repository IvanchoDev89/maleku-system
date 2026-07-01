from datetime import datetime
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.core.utils import escape_like_pattern
from app.models import Booking, BookingStatus, User

router = APIRouter(tags=["Super Admin - Bookings"])


class BookingListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    vendor_id: UUID | None = None
    property_id: UUID | None = None
    tour_id: UUID | None = None
    booking_type: str
    status: str
    guest_name: str
    guest_email: str
    total_amount: float = 0
    currency: str = "USD"
    created_at: datetime
    check_in: datetime | None = None
    check_out: datetime | None = None


class BookingListResponse(BaseModel):
    items: list[BookingListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class BookingDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    vendor_id: UUID | None = None
    property_id: UUID | None = None
    room_id: UUID | None = None
    tour_id: UUID | None = None
    booking_type: str
    status: str
    guest_name: str
    guest_email: str
    guest_phone: str | None = None
    guest_notes: str | None = None
    check_in: datetime | None = None
    check_out: datetime | None = None
    guests: int = 1
    participants: int = 1
    subtotal: float = 0
    commission_amount: float = 0
    total_amount: float = 0
    currency: str = "USD"
    confirmation_code: str | None = None
    cancellation_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: datetime | None = None
    cancelled_at: datetime | None = None


class BookingStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str


@router.get("", response_model=BookingListResponse)
async def list_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    booking_type: str | None = Query(None),
    search: str | None = Query(None),
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    count_query = select(func.count(Booking.id))
    query = select(Booking)

    if search:
        safe = escape_like_pattern(search)
        like = f"%{safe}%"
        query = query.where((Booking.guest_name.ilike(like)) | (Booking.guest_email.ilike(like)))
        count_query = count_query.where(
            (Booking.guest_name.ilike(like)) | (Booking.guest_email.ilike(like))
        )

    if status:
        query = query.where(Booking.status == status)
        count_query = count_query.where(Booking.status == status)

    if booking_type:
        query = query.where(Booking.booking_type == booking_type)
        count_query = count_query.where(Booking.booking_type == booking_type)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    query = query.order_by(desc(Booking.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    bookings = result.scalars().all()

    total_pages = max(1, ceil(total / page_size))

    items = [
        BookingListItem(
            id=b.id,
            user_id=b.user_id,
            vendor_id=b.vendor_id,
            property_id=b.property_id,
            tour_id=b.tour_id,
            booking_type=b.booking_type,
            status=b.status.value if b.status else "pending",
            guest_name=b.guest_name,
            guest_email=b.guest_email,
            total_amount=float(b.total_amount or 0),
            currency=b.currency or "USD",
            created_at=b.created_at,
            check_in=b.check_in,
            check_out=b.check_out,
        )
        for b in bookings
    ]

    return BookingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{booking_id}", response_model=BookingDetail)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return BookingDetail(
        id=booking.id,
        user_id=booking.user_id,
        vendor_id=booking.vendor_id,
        property_id=booking.property_id,
        room_id=booking.room_id,
        tour_id=booking.tour_id,
        booking_type=booking.booking_type,
        status=booking.status.value if booking.status else "pending",
        guest_name=booking.guest_name,
        guest_email=booking.guest_email,
        guest_phone=booking.guest_phone,
        guest_notes=booking.guest_notes,
        check_in=booking.check_in,
        check_out=booking.check_out,
        guests=booking.guests or 1,
        participants=booking.participants or 1,
        subtotal=float(booking.subtotal or 0),
        commission_amount=float(booking.commission_amount or 0),
        total_amount=float(booking.total_amount or 0),
        currency=booking.currency or "USD",
        confirmation_code=booking.confirmation_code,
        cancellation_reason=booking.cancellation_reason,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
        confirmed_at=booking.confirmed_at,
        cancelled_at=booking.cancelled_at,
    )


@router.put("/{booking_id}/status", response_model=dict)
@limiter.limit("10/minute")
async def update_booking_status(
    request: Request,
    booking_id: UUID,
    body: BookingStatusUpdate,
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    new_status = body.status.lower()
    try:
        booking.status = BookingStatus(new_status)
    except ValueError:
        valid = [s.value for s in BookingStatus]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{new_status}'. Must be one of: {valid}",
        )

    await db.commit()
    await db.refresh(booking)

    return {"message": "Status updated", "status": booking.status.value}


@router.delete(
    "/{booking_id}",
    response_model=dict,
    summary="Delete a booking",
    description="Permanently removes a booking record.",
)
@limiter.limit("10/minute")
async def delete_booking(
    request: Request,
    booking_id: UUID,
    current_user: User = Depends(require_superadmin()),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    await db.delete(booking)
    await db.commit()

    return {"success": True, "message": "Booking deleted successfully"}
