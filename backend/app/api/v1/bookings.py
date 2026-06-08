import uuid
import secrets
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select, func, text, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_db
from app.core.pagination import paginate_flat
from app.core.security import get_current_user, require_role
from app.core.config import settings
from app.models import User, UserRole, Vendor, Property, Room, Tour, Booking, BookingStatus
from app.schemas import (
    BookingResponse, BookingPropertyRequest, BookingTourRequest,
    BookingUpdateStatus, PaginationParams, PaginatedResponse,
    PricePreviewRequest, PricePreviewResponse
)
from app.services.pricing_service import calculate_room_price, calculate_tour_price, calculate_commission
from app.services.availability_service import check_room_availability, check_tour_availability
from app.services.email_service import email_service
from app.core.logging import get_logger

router = APIRouter(tags=["Bookings"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


def generate_confirmation_code():
    return f"CRT-{secrets.token_hex(4).upper()}"


def _generate_room_lock_key(room_id: uuid.UUID, check_in: datetime, check_out: datetime) -> int:
    """
    Genera un advisory lock key único para prevenir race conditions en bookings.
    Usa hash de room_id + fechas para crear un lock único por habitación/rango.
    """
    key_string = f"{room_id}:{check_in.date().isoformat()}:{check_out.date().isoformat()}"
    return int(hashlib.md5(key_string.encode()).hexdigest()[:8], 16) & 0x7FFFFFFF


@router.post("/property", response_model=BookingResponse,
             summary="Create property booking",
             description="Creates a new property/room booking with advisory lock to prevent race conditions. Calculates pricing with weekend rates, extra guests, and weekly discounts.")
async def create_property_booking(
    data: BookingPropertyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get property
    result = await db.execute(select(Property).where(Property.id == data.property_id))
    property_obj = result.scalar_one_or_none()
    
    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Validate dates
    nights = (data.check_out - data.check_in).days
    if nights < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum stay is 1 night"
        )
    
    if data.check_in < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in date cannot be in the past"
        )
    
    # Get room (REQUIRED for real pricing)
    if not data.room_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="room_id is required for property booking"
        )
    
    room_result = await db.execute(
        select(Room).where(
            Room.id == data.room_id,
            Room.property_id == data.property_id  # Ensure room belongs to property
        )
    )
    room = room_result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or does not belong to this property"
        )
    
    if not room.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is not available for booking"
        )
    
    # CRITICAL: Prevent race condition with PostgreSQL advisory lock
    # Generar lock key único para esta habitación y rango de fechas
    lock_key = _generate_room_lock_key(data.room_id, data.check_in, data.check_out)
    
    # Adquirir advisory lock (bloquea hasta que esté disponible)
    await db.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": lock_key})
    logger.debug(f"Acquired advisory lock {lock_key} for room {data.room_id}")
    
    # RE-VERIFICAR disponibilidad CON EL LOCK ADQUIRIDO
    # Esto previene TOCTOU: otro proceso no puede haber reservado mientras esperábamos
    is_available = await check_room_availability(
        db=db,
        room_id=data.room_id,
        check_in=data.check_in,
        check_out=data.check_out
    )
    
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Room is not available for the selected dates"
        )
    
    # Get vendor for commission
    vendor_result = await db.execute(select(Vendor).where(Vendor.id == property_obj.vendor_id))
    vendor = vendor_result.scalar_one_or_none()
    
    # Calculate pricing using real room rates
    try:
        pricing = calculate_room_price(
            room=room,
            check_in=data.check_in,
            check_out=data.check_out,
            guests=data.guests
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    subtotal = pricing["subtotal"]
    
    # Apply weekly discount from property settings if applicable
    if nights >= 7 and property_obj.weekly_discount > 0:
        discount_amount = subtotal * (property_obj.weekly_discount / 100)
        subtotal = round(subtotal - discount_amount, 2)
    
    commission_rate = vendor.commission_rate if vendor else settings.STRIPE_COMMISSION_RATE
    commission = calculate_commission(subtotal, commission_rate)
    total = subtotal  # Total before payment processing fees (added by Stripe)
    
    booking = Booking(
        user_id=current_user.id,
        vendor_id=property_obj.vendor_id,
        property_id=data.property_id,
        room_id=data.room_id,
        booking_type="property",
        status=BookingStatus.PENDING,
        check_in=data.check_in,
        check_out=data.check_out,
        guests=data.guests,
        guest_name=data.guest_name,
        guest_email=data.guest_email,
        guest_phone=data.guest_phone,
        guest_notes=data.guest_notes,
        subtotal=subtotal,
        commission_amount=commission,
        total_amount=total,
        currency=pricing["currency"],
        confirmation_code=generate_confirmation_code()
    )
    db.add(booking)
    await db.flush()
    await db.commit()
    
    # Send confirmation emails (async - don't block response)
    try:
        await _send_booking_confirmation_emails(db, booking, property_obj, room, current_user)
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error(f"Failed to send booking confirmation emails: {e}")
    
    return BookingResponse.model_validate(booking)


async def _send_booking_confirmation_emails(
    db: AsyncSession,
    booking: Booking,
    property_obj: Property,
    room: Room,
    user: User
):
    """Send booking confirmation emails to customer and vendor"""
    # Email to customer
    await email_service.send_booking_confirmation(
        to=user.email,
        booking_code=booking.confirmation_code,
        property_name=property_obj.name,
        check_in=booking.check_in.strftime("%Y-%m-%d"),
        check_out=booking.check_out.strftime("%Y-%m-%d"),
        total_amount=booking.total_amount,
        currency=booking.currency
    )
    logger.info(f"Booking confirmation email sent to customer: {user.email}")
    
    # Email to vendor
    if booking.vendor_id:
        vendor_result = await db.execute(
            select(Vendor).where(Vendor.id == booking.vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        
        if vendor and vendor.email:
            await email_service.send_booking_notification_to_vendor(
                to=vendor.email,
                business_name=vendor.business_name,
                booking_code=booking.confirmation_code,
                guest_name=booking.guest_name,
                check_in=booking.check_in.strftime("%Y-%m-%d"),
                check_out=booking.check_out.strftime("%Y-%m-%d"),
                total_amount=booking.total_amount
            )
            logger.info(f"Booking notification email sent to vendor: {vendor.email}")


@router.post("/tour", response_model=BookingResponse,
             summary="Create tour booking",
             description="Creates a new tour booking with advisory lock to prevent overbooking. Validates participants against max group size.")
async def create_tour_booking(
    data: BookingTourRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get tour
    result = await db.execute(select(Tour).where(Tour.id == data.tour_id))
    tour = result.scalar_one_or_none()
    
    if not tour:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tour not found"
        )
    
    if not tour.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tour is not available for booking"
        )
    
    # Validate participants against max group size
    if data.participants > tour.max_group_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {tour.max_group_size} participants allowed for this tour"
        )
    
    # Validate date is not in the past
    if data.booking_date < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking date cannot be in the past"
        )
    
    # CRITICAL: Prevent race condition with PostgreSQL advisory lock for tours
    # Generar lock key único para este tour y fecha
    tour_lock_key = _generate_room_lock_key(
        uuid.UUID(data.tour_id) if isinstance(data.tour_id, str) else data.tour_id,
        data.booking_date,
        data.booking_date
    )
    
    # Adquirir advisory lock (bloquea hasta que esté disponible)
    await db.execute(text("SELECT pg_advisory_xact_lock(:lock_key)"), {"lock_key": tour_lock_key})
    logger.debug(f"Acquired advisory lock {tour_lock_key} for tour {data.tour_id}")
    
    # RE-VERIFICAR disponibilidad CON EL LOCK ADQUIRIDO
    # Esto previene TOCTOU: otro proceso no puede haber reservado mientras esperábamos
    is_available, reason = await check_tour_availability(
        db=db,
        tour_id=data.tour_id,
        booking_date=data.booking_date,
        participants=data.participants
    )
    
    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=reason
        )
    
    # Get vendor for commission
    vendor_result = await db.execute(select(Vendor).where(Vendor.id == tour.vendor_id))
    vendor = vendor_result.scalar_one_or_none()
    
    # Calculate pricing using pricing service
    pricing = calculate_tour_price(tour=tour, participants=data.participants)
    subtotal = pricing["subtotal"]
    commission_rate = vendor.commission_rate if vendor else settings.STRIPE_COMMISSION_RATE
    commission = calculate_commission(subtotal, commission_rate)
    total = subtotal
    
    booking = Booking(
        user_id=current_user.id,
        vendor_id=tour.vendor_id,
        tour_id=data.tour_id,
        booking_type="tour",
        status=BookingStatus.PENDING,
        check_in=data.booking_date,
        participants=data.participants,
        guest_name=data.guest_name,
        guest_email=data.guest_email,
        guest_phone=data.guest_phone,
        guest_notes=data.guest_notes,
        subtotal=subtotal,
        commission_amount=commission,
        total_amount=total,
        currency=pricing["currency"],
        confirmation_code=generate_confirmation_code()
    )
    db.add(booking)
    await db.flush()
    await db.commit()
    
    # Send confirmation emails for tour booking
    try:
        await _send_tour_booking_emails(db, booking, tour, current_user)
    except (RuntimeError, ConnectionError, ValueError) as e:
        logger.error(f"Failed to send tour booking confirmation emails: {e}")
    
    return BookingResponse.model_validate(booking)


async def _send_tour_booking_emails(
    db: AsyncSession,
    booking: Booking,
    tour: Tour,
    user: User
):
    """Send tour booking confirmation emails"""
    # Email to customer
    await email_service.send_email(
        to=user.email,
        subject=f"Tour Booking Confirmed - {booking.confirmation_code}",
        html=f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #1e7a67;">Tour Booking Confirmed</h1>
                
                <p>Your tour has been booked!</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Tour Details</h3>
                    <p><strong>Confirmation Code:</strong> {booking.confirmation_code}</p>
                    <p><strong>Tour:</strong> {tour.name}</p>
                    <p><strong>Date:</strong> {booking.check_in.strftime("%Y-%m-%d")}</p>
                    <p><strong>Participants:</strong> {booking.participants}</p>
                    <p><strong>Total:</strong> {booking.currency} ${booking.total_amount:.2f}</p>
                </div>
                
                <p>Thank you for choosing Costa Rica Travel!</p>
            </div>
        </body>
        </html>
        """
    )
    logger.info(f"Tour confirmation email sent to: {user.email}")
    
    # Email to vendor
    if booking.vendor_id:
        vendor_result = await db.execute(
            select(Vendor).where(Vendor.id == booking.vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        
        if vendor and vendor.email:
            await email_service.send_booking_notification_to_vendor(
                to=vendor.email,
                business_name=vendor.business_name,
                booking_code=booking.confirmation_code,
                guest_name=booking.guest_name,
                check_in=booking.check_in.strftime("%Y-%m-%d"),
                check_out=booking.check_in.strftime("%Y-%m-%d"),  # Same day for tours
                total_amount=booking.total_amount
            )
            logger.info(f"Tour booking notification sent to vendor: {vendor.email}")


@router.get("", response_model=PaginatedResponse,
            summary="List bookings",
            description="Returns paginated bookings scoped to the authenticated user/role: CLIENT sees own, VENDOR sees their property/tour bookings, ADMIN/SUPER_ADMIN sees all.")
async def get_bookings(
    params: PaginationParams = Depends(),
    status: str = None,
    booking_type: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Base query - users see their own, vendors see theirs, admins see all
    if current_user.role == UserRole.CLIENT:
        query = select(Booking).where(Booking.user_id == current_user.id)
    elif current_user.role == UserRole.VENDOR:
        vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
        vendor = vendor_result.scalar_one_or_none()
        if vendor:
            query = select(Booking).where(Booking.vendor_id == vendor.id)
        else:
            query = select(Booking).where(Booking.id is None)  # Empty
    elif current_user.role in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
        query = select(Booking)
    else:
        query = select(Booking).where(Booking.id is None)  # Empty for other roles
    
    if status:
        query = query.where(Booking.status == status)
    if booking_type:
        query = query.where(Booking.booking_type == booking_type)
    
    # Apply eager loading to avoid N+1 queries
    query = query.options(
        selectinload(Booking.user),
        selectinload(Booking.vendor),
        selectinload(Booking.property),
        selectinload(Booking.room),
        selectinload(Booking.tour)
    )
    
    response = await paginate_flat(
        db, query, params,
        transform_func=BookingResponse.model_validate,
        order_by=Booking.created_at.desc()
    )
    
    return PaginatedResponse(**response)


@router.post("/preview", response_model=PricePreviewResponse)
@limiter.limit("30/minute")  # Rate limiting: 30 previews por minuto por IP
async def preview_price(
    request: Request,
    data: PricePreviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview price breakdown for a room booking without creating a booking.
    Useful for showing price details before user confirms.
    """
    # Get room
    room_result = await db.execute(
        select(Room).where(Room.id == data.room_id)
    )
    room = room_result.scalar_one_or_none()
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Get property for weekly discount
    property_result = await db.execute(
        select(Property).where(Property.id == room.property_id)
    )
    property_obj = property_result.scalar_one_or_none()
    
    # Validate dates
    nights = (data.check_out - data.check_in).days
    if nights < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minimum stay is 1 night"
        )
    
    # Calculate pricing
    try:
        pricing = calculate_room_price(
            room=room,
            check_in=data.check_in,
            check_out=data.check_out,
            guests=data.guests
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    subtotal = pricing["subtotal"]
    weekly_discount_percent = 0
    weekly_discount_amount = 0
    
    # Apply weekly discount
    if nights >= 7 and property_obj and property_obj.weekly_discount > 0:
        weekly_discount_percent = property_obj.weekly_discount
        weekly_discount_amount = subtotal * (weekly_discount_percent / 100)
        subtotal = round(subtotal - weekly_discount_amount, 2)
    
    # Get vendor for commission calculation
    commission = 0
    if property_obj:
        vendor_result = await db.execute(
            select(Vendor).where(Vendor.id == property_obj.vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        if vendor:
            commission = calculate_commission(subtotal, vendor.commission_rate)
    
    return PricePreviewResponse(
        nights=pricing["nights"],
        weekday_nights=pricing["weekday_nights"],
        weekend_nights=pricing["weekend_nights"],
        weekday_price=pricing["weekday_price"],
        weekend_price=pricing["weekend_price"],
        weekday_total=pricing["weekday_total"],
        weekend_total=pricing["weekend_total"],
        base_subtotal=pricing["base_subtotal"],
        guests=pricing["guests"],
        max_occupancy=pricing["max_occupancy"],
        extra_guests=pricing["extra_guests"],
        extra_guest_price=pricing["extra_guest_price"],
        extra_guests_total=pricing["extra_guests_total"],
        weekly_discount_percent=weekly_discount_percent,
        weekly_discount_amount=weekly_discount_amount,
        subtotal=subtotal,
        commission_amount=commission,
        total=subtotal,
        currency=pricing["currency"]
    )


@router.get("/{booking_id}", response_model=BookingResponse,
            summary="Get booking by ID",
            description="Returns a single booking with all relations (user, vendor, property, room, tour). Access scoped by role.")
async def get_booking(
    booking_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.vendor),
            selectinload(Booking.property),
            selectinload(Booking.room),
            selectinload(Booking.tour)
        )
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check access
    if current_user.role == UserRole.CLIENT and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    if current_user.role == UserRole.VENDOR:
        vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
        vendor = vendor_result.scalar_one_or_none()
        if not vendor or booking.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
    
    return BookingResponse.model_validate(booking)


@router.put("/{booking_id}/status", response_model=BookingResponse,
            summary="Update booking status",
            description="Updates booking status. VENDOR can confirm/cancel. CLIENT can only cancel their own bookings.")
async def update_booking_status(
    booking_id: uuid.UUID,
    data: BookingUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.vendor),
            selectinload(Booking.property),
            selectinload(Booking.room),
            selectinload(Booking.tour)
        )
        .where(Booking.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check access
    if current_user.role == UserRole.VENDOR:
        vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
        vendor = vendor_result.scalar_one_or_none()
        if not vendor or booking.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        # Vendors can only confirm or cancel
        if data.status not in ["confirmed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendors can only confirm or cancel bookings"
            )
    elif current_user.role == UserRole.CLIENT:
        if current_user.id != booking.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        if data.status != "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Clients can only cancel bookings"
            )
    
    try:
        booking.status = BookingStatus(data.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status"
        )
    
    await db.flush()
    await db.commit()
    
    return BookingResponse.model_validate(booking)


@router.get("/vendor/stats",
            summary="Vendor booking statistics",
            description="Returns aggregated booking stats for the authenticated vendor: total, pending, confirmed, completed, cancelled counts plus revenue and commission totals.")
async def get_vendor_booking_stats(
    current_user: User = Depends(require_role(UserRole.VENDOR)),
    db: AsyncSession = Depends(get_db)
):
    vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = vendor_result.scalar_one_or_none()
    
    if not vendor:
        return {"error": "Vendor not found"}
    
    # Get stats using database aggregation (no N+1)
    stats_result = await db.execute(
        select(
            func.count(Booking.id).label('total'),
            func.sum(case((Booking.status == BookingStatus.PENDING, 1), else_=0)).label('pending'),
            func.sum(case((Booking.status == BookingStatus.CONFIRMED, 1), else_=0)).label('confirmed'),
            func.sum(case((Booking.status == BookingStatus.COMPLETED, 1), else_=0)).label('completed'),
            func.sum(case((Booking.status == BookingStatus.CANCELLED, 1), else_=0)).label('cancelled'),
            func.coalesce(func.sum(case((Booking.status == BookingStatus.COMPLETED, Booking.total_amount), else_=0)), 0).label('total_revenue'),
            func.coalesce(func.sum(case((Booking.status == BookingStatus.COMPLETED, Booking.commission_amount), else_=0)), 0).label('total_commission')
        ).where(Booking.vendor_id == vendor.id)
    )
    stats = stats_result.one()
    
    return {
        "total_bookings": stats.total or 0,
        "pending": stats.pending or 0,
        "confirmed": stats.confirmed or 0,
        "completed": stats.completed or 0,
        "cancelled": stats.cancelled or 0,
        "total_revenue": float(stats.total_revenue or 0),
        "total_commission": float(stats.total_commission or 0)
    }


@router.get("/vendor/my-bookings", response_model=PaginatedResponse,
            summary="Vendor my bookings",
            description="Returns the authenticated vendor's bookings with optional status filter and pagination.")
async def get_vendor_my_bookings(
    params: PaginationParams = Depends(),
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource"
        )
    
    vendor_result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = vendor_result.scalar_one_or_none()
    
    if not vendor:
        return PaginatedResponse(
            items=[], total=0, page=params.page, page_size=params.page_size,
            total_pages=0, has_next=False, has_prev=False
        )
    
    query = select(Booking).where(Booking.vendor_id == vendor.id)
    
    if status:
        query = query.where(Booking.status == status)
    
    response = await paginate_flat(
        db, query, params,
        transform_func=BookingResponse.model_validate,
        order_by=Booking.created_at.desc()
    )
    
    return PaginatedResponse(**response)