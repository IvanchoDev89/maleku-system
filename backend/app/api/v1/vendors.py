import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import get_current_user, require_role, get_current_user_optional
from app.models import User, UserRole, Vendor, Property, Tour, Booking, BookingStatus, Review
from app.models import Vehicle, Boat, Transportation
from app.schemas import VendorResponse, VendorUpdate, VendorPublicResponse
from app.schemas.landing import VendorLandingResponse, LandingPropertyItem, LandingTourItem
from app.schemas.landing import LandingVehicleItem, LandingBoatItem, LandingTransportItem
from app.schemas.landing import LandingReview, LandingStats, LandingRanking
from app.services.cache_service import cache
from app.services.vendor_service import VendorService

router = APIRouter(tags=["Vendors"])

CACHE_TTL_LIST = 300  # 5 minutes for vendor lists
CACHE_TTL_DETAIL = 600  # 10 minutes for vendor details


@router.get(
    "",
    response_model=list[VendorPublicResponse],
    summary="List vendors",
    description="Returns a list of active vendors sorted by rating. Supports limit and offset for pagination.",
)
async def get_vendors(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0,
):
    cache_key = f"vendors:list:{limit}:{offset}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return [VendorPublicResponse(**item) for item in cached]

    result = await db.execute(
        select(Vendor)
        .where(Vendor.is_active)
        .order_by(Vendor.rating.desc())
        .offset(offset)
        .limit(limit)
    )
    vendors = result.scalars().all()
    response = [VendorPublicResponse.model_validate(v) for v in vendors]

    # Cache the response
    await cache.set(
        cache_key,
        [item.model_dump() for item in response],
        ttl=CACHE_TTL_LIST,
        tags=["vendors"],
    )

    return response


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor by ID",
    description="Returns a single vendor by UUID with full details including reviews and commission rate.",
)
async def get_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cache_key = f"vendors:detail:{vendor_id}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return VendorResponse(**cached)

    vendor = await VendorService.get_or_404(db, vendor_id)

    response = VendorResponse.model_validate(vendor)
    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["vendors", f"vendor:{vendor_id}"],
    )

    return response


@router.get(
    "/slug/{slug}",
    response_model=VendorResponse,
    summary="Get vendor by slug",
    description="Returns a single vendor by their business URL-friendly slug.",
)
async def get_vendor_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"vendors:slug:{slug}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        return VendorResponse(**cached)

    result = await db.execute(select(Vendor).where(Vendor.business_slug == slug))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    response = VendorResponse.model_validate(vendor)
    await cache.set(
        cache_key,
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["vendors", f"vendor:{vendor.id}"],
    )

    return response


@router.get(
    "/slug/{slug}/landing",
    response_model=VendorLandingResponse,
    summary="Get vendor landing page data",
    description="Returns all data needed for the public vendor/agency landing page: vendor info, services, reviews, stats, and ranking.",
)
async def get_vendor_landing(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    result = await db.execute(
        select(Vendor).options(
            joinedload(Vendor.properties),
            joinedload(Vendor.tours),
        ).where(Vendor.business_slug == slug)
    )
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    TOP_N = 5

    # Properties
    prop_query = (
        select(Property)
        .where(Property.vendor_id == vendor.id, Property.is_active == True)
        .order_by(Property.rating.desc())
    )
    prop_result = await db.execute(prop_query)
    all_properties = prop_result.scalars().all()
    properties = [LandingPropertyItem.model_validate(p) for p in all_properties[:TOP_N]]
    properties_has_more = len(all_properties) > TOP_N

    # Tours
    tour_query = (
        select(Tour)
        .where(Tour.vendor_id == vendor.id, Tour.is_active == True)
        .order_by(Tour.rating.desc())
    )
    tour_result = await db.execute(tour_query)
    all_tours = tour_result.scalars().all()
    tours = [LandingTourItem.model_validate(t) for t in all_tours[:TOP_N]]
    tours_has_more = len(all_tours) > TOP_N

    # Vehicles
    veh_result = await db.execute(
        select(Vehicle).where(Vehicle.vendor_id == vendor.id, Vehicle.is_active == True)
        .order_by(Vehicle.rating.desc())
    )
    all_vehicles = veh_result.scalars().all()
    vehicles = [LandingVehicleItem.model_validate(v) for v in all_vehicles[:TOP_N]]
    vehicles_has_more = len(all_vehicles) > TOP_N

    # Boats
    boat_result = await db.execute(
        select(Boat).where(Boat.vendor_id == vendor.id, Boat.is_active == True)
        .order_by(Boat.rating.desc())
    )
    all_boats = boat_result.scalars().all()
    boats = [LandingBoatItem.model_validate(b) for b in all_boats[:TOP_N]]
    boats_has_more = len(all_boats) > TOP_N

    # Transportation
    trans_result = await db.execute(
        select(Transportation).where(Transportation.vendor_id == vendor.id, Transportation.is_active == True)
        .order_by(Transportation.rating.desc())
    )
    all_trans = trans_result.scalars().all()
    transportation = [LandingTransportItem.model_validate(t) for t in all_trans[:TOP_N]]
    transportation_has_more = len(all_trans) > TOP_N

    # Reviews — get reviews for this vendor's properties and tours
    prop_ids = [p.id for p in all_properties]
    tour_ids = [t.id for t in all_tours]
    review_conditions = []
    if prop_ids:
        review_conditions.append(Review.property_id.in_(prop_ids))
    if tour_ids:
        review_conditions.append(Review.tour_id.in_(tour_ids))
    reviews = []
    reviews_total = 0
    reviews_avg = 0.0
    if review_conditions:
        review_query = (
            select(Review)
            .options(joinedload(Review.user))
            .where(
                or_(*review_conditions),
                Review.is_approved == True,
                Review.deleted_at == None,
            )
            .order_by(Review.created_at.desc())
        )
        review_result = await db.execute(review_query)
        all_reviews = review_result.scalars().all()
        reviews_total = len(all_reviews)
        if reviews_total > 0:
            reviews_avg = sum(r.rating for r in all_reviews) / reviews_total
        for r in all_reviews[:10]:
            lr = LandingReview.model_validate(r)
            lr.user_name = r.user.full_name if r.user else "Anonymous"
            reviews.append(lr)

    # Booking stats
    booking_result = await db.execute(
        select(func.count(Booking.id)).where(
            Booking.vendor_id == vendor.id
        )
    )
    total_bookings = booking_result.scalar() or 0

    # Ranking
    rank_result = await db.execute(
        select(func.count(Vendor.id)).where(
            Vendor.is_active == True,
            Vendor.rating > vendor.rating,
        )
    )
    higher_ranked = rank_result.scalar() or 0
    total_active = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.is_active == True)
    )
    total_active_count = total_active.scalar() or 0

    stats = LandingStats(
        total_properties=len(all_properties),
        total_tours=len(all_tours),
        total_vehicles=len(all_vehicles),
        total_boats=len(all_boats),
        total_transportation=len(all_trans),
        total_reviews=vendor.total_reviews or 0,
        total_bookings=total_bookings,
        member_since=vendor.created_at,
    )

    ranking = LandingRanking(
        position=higher_ranked + 1,
        total_vendors=total_active_count,
    )

    can_review = False
    eligible_booking_ids: list[str] = []
    if current_user and current_user.id != vendor.user_id:
        eligible = await db.execute(
            select(Booking).where(
                Booking.user_id == current_user.id,
                Booking.vendor_id == vendor.id,
                Booking.status == BookingStatus.COMPLETED,
                ~Booking.id.in_(select(Review.booking_id).where(Review.booking_id.isnot(None))),
            )
        )
        eligible_bookings = eligible.scalars().all()
        can_review = len(eligible_bookings) > 0
        eligible_booking_ids = [str(b.id) for b in eligible_bookings]

    return VendorLandingResponse(
        id=vendor.id,
        business_name=vendor.business_name,
        business_slug=vendor.business_slug,
        business_type=vendor.business_type,
        description=vendor.description,
        logo_url=vendor.logo_url,
        cover_image=vendor.cover_image,
        phone=vendor.phone,
        email=vendor.email,
        address=vendor.address,
        rating=vendor.rating,
        total_reviews=vendor.total_reviews or 0,
        is_verified=vendor.is_verified,
        properties=properties,
        properties_has_more=properties_has_more,
        tours=tours,
        tours_has_more=tours_has_more,
        vehicles=vehicles,
        vehicles_has_more=vehicles_has_more,
        boats=boats,
        boats_has_more=boats_has_more,
        transportation=transportation,
        transportation_has_more=transportation_has_more,
        reviews=reviews,
        reviews_total=reviews_total,
        reviews_average_rating=round(reviews_avg, 1),
        stats=stats,
        ranking=ranking,
        can_review=can_review,
        eligible_booking_ids=eligible_booking_ids,
    )


@router.get(
    "/me/profile",
    response_model=VendorResponse,
    summary="Get my vendor profile",
    description="Returns the authenticated vendor's own profile.",
)
async def get_my_vendor_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource",
        )

    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found"
        )

    return VendorResponse.model_validate(vendor)


@router.put(
    "/me/profile",
    response_model=VendorResponse,
    summary="Update vendor profile",
    description="Updates the authenticated vendor's profile. Only allows specific fields (business_name, description, phone, address, etc.) to prevent mass assignment.",
)
@limiter.limit("10/minute")
async def update_my_vendor_profile(
    request: Request,
    data: VendorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource",
        )

    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found"
        )

    # SECURITY: Prevent mass assignment - only allow specific fields
    allowed_fields = {
        "business_name",
        "description",
        "phone",
        "address",
        "city",
        "country",
        "website",
        "logo_url",
        "tax_id",
    }

    for field, value in data.model_dump(exclude_unset=True).items():
        if field in allowed_fields:
            setattr(vendor, field, value)

    await db.flush()
    await db.commit()

    await VendorService.invalidate_cache(vendor.id, vendor.business_slug)

    return VendorResponse.model_validate(vendor)


@router.get(
    "/me/analytics",
    response_model=dict,
    summary="Vendor analytics dashboard",
    description="Returns key metrics for the authenticated vendor: property count, tour count, booking stats (pending/confirmed/completed), revenue, rating, and commission rate.",
)
async def get_my_analytics(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only vendors can access this resource",
        )

    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found"
        )

    # Get property count
    prop_result = await db.execute(
        select(func.count()).where(Property.vendor_id == vendor.id)
    )
    total_properties = prop_result.scalar() or 0

    tour_result = await db.execute(
        select(func.count()).where(Tour.vendor_id == vendor.id)
    )
    total_tours = tour_result.scalar() or 0

    # Get bookings (still need full rows for aggregation)
    booking_result = await db.execute(
        select(Booking).where(Booking.vendor_id == vendor.id)
    )
    bookings = booking_result.scalars().all()

    pending = sum(1 for b in bookings if b.status == BookingStatus.PENDING)
    confirmed = sum(1 for b in bookings if b.status == BookingStatus.CONFIRMED)
    completed = sum(1 for b in bookings if b.status == BookingStatus.COMPLETED)
    total_revenue = sum(
        b.total_amount for b in bookings if b.status == BookingStatus.COMPLETED
    )

    return {
        "total_properties": total_properties,
        "total_tours": total_tours,
        "total_bookings": len(bookings),
        "pending_bookings": pending,
        "confirmed_bookings": confirmed,
        "completed_bookings": completed,
        "total_revenue": total_revenue,
        "rating": vendor.rating,
        "total_reviews": vendor.total_reviews,
        "commission_rate": vendor.commission_rate,
    }


@router.put(
    "/{vendor_id}/verify",
    response_model=dict,
    summary="Verify vendor",
    description="Marks a vendor as verified. SUPER_ADMIN role required.",
)
@limiter.limit("10/minute")
async def verify_vendor(
    request: Request,
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
):
    vendor = await VendorService.get_or_404(db, vendor_id)

    vendor.is_verified = True
    await db.flush()
    await db.commit()

    await VendorService.invalidate_cache(vendor.id, vendor.business_slug)

    return {"message": "Vendor verified successfully"}


@router.put(
    "/{vendor_id}/activate",
    response_model=dict,
    summary="Toggle vendor active status",
    description="Activates or deactivates a vendor account. SUPER_ADMIN role required.",
)
@limiter.limit("10/minute")
async def toggle_vendor_active(
    request: Request,
    vendor_id: uuid.UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.SUPER_ADMIN)),
):
    vendor = await VendorService.get_or_404(db, vendor_id)

    vendor.is_active = is_active
    await db.flush()
    await db.commit()

    await VendorService.invalidate_cache(vendor.id, vendor.business_slug)

    return {"message": f"Vendor {'activated' if is_active else 'deactivated'}"}
