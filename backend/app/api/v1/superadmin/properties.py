from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.core.utils import escape_like_pattern
from app.models import Property, Room, User, Vendor
from app.schemas import PropertyCreate, PropertyListResponse, PropertyResponse, PropertyUpdate

router = APIRouter(prefix="/properties", tags=["Super Admin - Properties"])


class SuperAdminPropertyCreate(PropertyCreate):
    vendor_id: UUID


class RoomCreate(BaseModel):
    name: str
    description: str | None = None
    max_guests: int = 2
    beds: int = 1
    bed_type: str | None = None
    price_per_night: float = 0
    weekend_price: float = 0
    extra_guest_price: float = 0
    cleaning_fee: float = 0
    images: list[str] = []
    is_available: bool = True


class RoomUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    max_guests: int | None = None
    beds: int | None = None
    bed_type: str | None = None
    price_per_night: float | None = None
    weekend_price: float | None = None
    extra_guest_price: float | None = None
    cleaning_fee: float | None = None
    images: list[str] | None = None
    is_available: bool | None = None


@router.get("", response_model=dict)
async def list_properties(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    property_type: str | None = Query(None),
    is_active: bool | None = Query(None),
    is_featured: bool | None = Query(None),
    is_verified: bool | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    count_query = select(func.count(Property.id))
    query = select(Property)

    if search:
        safe = escape_like_pattern(search)
        like = f"%{safe}%"
        query = query.where(
            (Property.name.ilike(like))
            | (Property.city.ilike(like))
            | (Property.region.ilike(like))
        )
        count_query = count_query.where(
            (Property.name.ilike(like))
            | (Property.city.ilike(like))
            | (Property.region.ilike(like))
        )

    if property_type:
        query = query.where(Property.property_type == property_type)
        count_query = count_query.where(Property.property_type == property_type)

    if is_active is not None:
        query = query.where(Property.is_active == is_active)
        count_query = count_query.where(Property.is_active == is_active)

    if is_featured is not None:
        query = query.where(Property.is_featured == is_featured)
        count_query = count_query.where(Property.is_featured == is_featured)

    if is_verified is not None:
        query = query.where(Property.is_verified == is_verified)
        count_query = count_query.where(Property.is_verified == is_verified)

    result = await db.execute(count_query)
    total = result.scalar() or 0

    sort_col = getattr(Property, sort_by, Property.created_at)
    order_fn = desc if sort_order == "desc" else lambda c: c
    query = query.order_by(order_fn(sort_col))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    properties = result.scalars().all()

    total_pages = max(1, (total + page_size - 1) // page_size)

    return {
        "items": [PropertyListResponse.model_validate(p).model_dump() for p in properties],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(
        select(Property)
        .options(selectinload(Property.rooms), selectinload(Property.vendor))
        .where(Property.id == property_id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return PropertyResponse.model_validate(prop)


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_property(
    request: Request,
    data: SuperAdminPropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    import uuid as _uuid

    vendor_id = data.vendor_id

    v_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    if not v_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Vendor not found")

    base_slug = data.name.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(_uuid.uuid4())[:8]}"

    prop = Property(
        vendor_id=vendor_id,
        name=data.name,
        slug=slug,
        short_description=data.short_description,
        description=data.description,
        property_type=data.property_type,
        category=data.category,
        address=data.address,
        country=data.country,
        province=data.province,
        region=data.region,
        city=data.city,
        district=data.district,
        latitude=data.latitude,
        longitude=data.longitude,
        cover_image=data.cover_image,
        images=data.images or [],
        amenities=data.amenities or [],
        features=data.features or [],
        check_in_time=data.check_in_time,
        check_out_time=data.check_out_time,
        cancellation_policy=data.cancellation_policy,
        house_rules=data.house_rules,
        min_guests=data.min_guests,
        max_guests=data.max_guests,
        beds=data.beds,
        baths=data.baths,
        base_price=data.base_price,
        currency=data.currency,
        weekend_price=data.weekend_price,
        weekly_discount=data.weekly_discount,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(prop)
    await db.flush()

    for room_data in data.rooms or []:
        room = Room(
            property_id=prop.id,
            name=room_data.get("name", "Room"),
            description=room_data.get("description"),
            max_guests=room_data.get("max_guests", 2),
            beds=room_data.get("beds", 1),
            bed_type=room_data.get("bed_type"),
            price_per_night=room_data.get("price_per_night", 0),
            weekend_price=room_data.get("weekend_price", 0),
            extra_guest_price=room_data.get("extra_guest_price", 0),
            cleaning_fee=room_data.get("cleaning_fee", 0),
            images=room_data.get("images", []),
            is_available=room_data.get("is_available", True),
        )
        db.add(room)

    await db.commit()
    await db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.put("/{property_id}", response_model=PropertyResponse)
@limiter.limit("10/minute")
async def update_property(
    request: Request,
    property_id: UUID,
    data: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(
        select(Property)
        .options(selectinload(Property.rooms), selectinload(Property.vendor))
        .where(Property.id == property_id)
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    update_data = data.model_dump(exclude_unset=True)
    allowed_fields = {
        "name",
        "slug",
        "short_description",
        "description",
        "property_type",
        "category",
        "address",
        "country",
        "province",
        "region",
        "city",
        "district",
        "latitude",
        "longitude",
        "map_address",
        "cover_image",
        "images",
        "videos",
        "virtual_tour_url",
        "amenities",
        "features",
        "check_in_time",
        "check_out_time",
        "cancellation_policy",
        "house_rules",
        "important_info",
        "min_guests",
        "max_guests",
        "beds",
        "baths",
        "square_meters",
        "base_price",
        "currency",
        "weekend_price",
        "weekly_discount",
        "seo_title",
        "seo_description",
        "seo_keywords",
        "is_featured",
        "is_active",
        "is_verified",
    }
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(prop, key, value)

    prop.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.delete("/{property_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_property(
    request: Request,
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    await db.delete(prop)
    await db.commit()
    return {"success": True, "message": "Property deleted successfully"}


@router.post("/{property_id}/feature", response_model=dict)
@limiter.limit("10/minute")
async def toggle_property_featured(
    request: Request,
    property_id: UUID,
    featured: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    prop.is_featured = featured
    prop.updated_at = datetime.now(UTC)
    await db.commit()
    return {
        "success": True,
        "is_featured": prop.is_featured,
        "message": f"Property {'featured' if featured else 'unfeatured'} successfully",
    }


# --- Room management ---


@router.get("/{property_id}/rooms", response_model=list[dict])
async def list_rooms(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Property not found")

    rooms_result = await db.execute(
        select(Room).where(Room.property_id == property_id).order_by(Room.name)
    )
    rooms = rooms_result.scalars().all()
    return [
        {
            "id": str(r.id),
            "property_id": str(r.property_id),
            "name": r.name,
            "description": r.description,
            "max_guests": r.max_guests,
            "beds": r.beds,
            "bed_type": r.bed_type,
            "price_per_night": float(r.price_per_night or 0),
            "weekend_price": float(r.weekend_price or 0),
            "extra_guest_price": float(r.extra_guest_price or 0),
            "cleaning_fee": float(r.cleaning_fee or 0),
            "images": r.images or [],
            "is_available": r.is_available,
        }
        for r in rooms
    ]


@router.post("/{property_id}/rooms", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_room(
    request: Request,
    property_id: UUID,
    data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    p_result = await db.execute(select(Property).where(Property.id == property_id))
    if not p_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Property not found")

    room = Room(
        property_id=property_id,
        name=data.name,
        description=data.description,
        max_guests=data.max_guests,
        beds=data.beds,
        bed_type=data.bed_type,
        price_per_night=data.price_per_night,
        weekend_price=data.weekend_price,
        extra_guest_price=data.extra_guest_price,
        cleaning_fee=data.cleaning_fee,
        images=data.images,
        is_available=data.is_available,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return {
        "success": True,
        "id": str(room.id),
        "message": "Room created successfully",
    }


@router.put("/{property_id}/rooms/{room_id}", response_model=dict)
@limiter.limit("10/minute")
async def update_room(
    request: Request,
    property_id: UUID,
    room_id: UUID,
    data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(
        select(Room).where(Room.id == room_id, Room.property_id == property_id)
    )
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(room, key, value)

    await db.commit()
    return {"success": True, "message": "Room updated successfully"}


@router.delete("/{property_id}/rooms/{room_id}", response_model=dict)
@limiter.limit("10/minute")
async def delete_room(
    request: Request,
    property_id: UUID,
    room_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    result = await db.execute(
        select(Room).where(Room.id == room_id, Room.property_id == property_id)
    )
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    await db.delete(room)
    await db.commit()
    return {"success": True, "message": "Room deleted successfully"}
