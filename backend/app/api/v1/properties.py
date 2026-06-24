import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Request,
)
from sqlalchemy import select
from app.core.rate_limiter import limiter
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.pagination import paginate_flat
from app.core.security import get_current_user, require_permission
from app.models import User, UserRole, Vendor, Property
from app.models.property import PropertyType, PropertyCategory
from app.schemas import (
    PropertyResponse,
    PropertyCreate,
    PropertyUpdate,
    PropertyListResponse,
    PaginationParams,
    PaginatedResponse,
)
from app.services.cache_service import cache
from app.services.cloudinary_service import cloudinary_service, CloudinaryError

from app.api.v1.upload import (
    validate_file,
    validate_image_bytes,
    save_upload_file,
    upload_to_cloudinary,
    MAX_FILE_SIZE,
)

logger = get_logger(__name__)

router = APIRouter(tags=["Properties"])

CACHE_TTL_LIST = 300
CACHE_TTL_DETAIL = 600
CACHE_TTL_FEATURED = 180

ALLOWED_FIELDS = {
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
    "is_active",
    "is_featured",
}


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List properties",
    description="Paginated list of active properties with optional filters by region, type, category, price range, rating, and featured status.",
)
async def get_properties(
    params: PaginationParams = Depends(),
    region: str = None,
    property_type: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    rating: float = None,
    featured: bool = None,
    db: AsyncSession = Depends(get_db),
):
    # Generate cache key based on query parameters
    cache_key = f"properties:list:{region}:{property_type}:{category}:{min_price}:{max_price}:{rating}:{featured}:{params.page}:{params.page_size}"

    # Try to get from cache
    cached = await cache.get(cache_key)
    if cached:
        return PaginatedResponse(**cached)

    # Build query with eager loading
    query = select(Property).where(Property.is_active)
    query = query.options(selectinload(Property.rooms))

    if region:
        query = query.where(Property.region == region)
    if property_type:
        query = query.where(Property.property_type == PropertyType(property_type))
    if category:
        query = query.where(Property.category == PropertyCategory(category))
    if min_price is not None:
        query = query.where(Property.base_price >= min_price)
    if max_price is not None:
        query = query.where(Property.base_price <= max_price)
    if rating:
        query = query.where(Property.rating >= rating)
    if featured:
        query = query.where(Property.is_featured)

    response = await paginate_flat(
        db,
        query,
        params,
        transform_func=PropertyListResponse.model_validate,
        order_by=Property.created_at.desc(),
    )

    # Cache the response
    await cache.set(
        cache_key, response.model_dump(), ttl=CACHE_TTL_LIST, tags=["properties"]
    )

    return response


@router.get(
    "/vendor/my",
    response_model=PaginatedResponse,
    summary="Get my properties (vendor)",
    description="Returns the authenticated vendor's own properties with pagination.",
)
async def get_my_properties(
    params: PaginationParams = Depends(),
    current_user: User = Depends(require_permission("properties", "read")),
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
        return PaginatedResponse(
            items=[],
            total=0,
            page=params.page,
            page_size=params.page_size,
            total_pages=0,
            has_next=False,
            has_prev=False,
        )

    query = select(Property).where(Property.vendor_id == vendor.id)
    query = query.options(selectinload(Property.rooms))

    response = await paginate_flat(
        db,
        query,
        params,
        transform_func=PropertyListResponse.model_validate,
        order_by=Property.created_at.desc(),
    )

    return response


@router.get(
    "/regions",
    response_model=dict,
    summary="List property regions",
    description="Returns a distinct list of all regions where active properties are located.",
)
async def get_regions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Property.region).where(Property.is_active).distinct()
    )
    regions = [r[0] for r in result.all() if r[0]]
    return {"regions": regions}


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Get property by ID",
    description="Returns a single property with all rooms, vendor info and reviews by its UUID.",
)
async def get_property(property_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Try to get from cache
    cache_key = f"properties:detail:{property_id}"
    cached = await cache.get(cache_key)
    if cached:
        return PropertyResponse(**cached)

    # Query with eager loading for all relationships
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.rooms),
            selectinload(Property.vendor),
            selectinload(Property.reviews),
        )
        .where(Property.id == property_id)
    )
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
        )

    response = PropertyResponse.model_validate(property_obj)
    await cache.set(
        cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["properties"]
    )
    return response


@router.get(
    "/slug/{slug}",
    response_model=PropertyResponse,
    summary="Get property by slug",
    description="Returns a single property by its URL-friendly slug with full details.",
)
async def get_property_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    # Try to get from cache
    cache_key = f"properties:slug:{slug}"
    cached = await cache.get(cache_key)
    if cached:
        return PropertyResponse(**cached)

    # Query with eager loading
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.rooms),
            selectinload(Property.vendor),
            selectinload(Property.reviews),
        )
        .where(Property.slug == slug)
    )
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
        )

    response = PropertyResponse.model_validate(property_obj)

    # Cache the response
    await cache.set(
        cache_key, response.model_dump(), ttl=CACHE_TTL_DETAIL, tags=["properties"]
    )

    return response


@router.post(
    "",
    response_model=PropertyResponse,
    summary="Create property",
    description="Creates a new property listing. Vendor or SUPER_ADMIN role required.",
)
@limiter.limit("10/minute")
async def create_property(
    request: Request,
    data: PropertyCreate,
    current_user: User = Depends(require_permission("properties", "create")),
    db: AsyncSession = Depends(get_db),
):
    # Get vendor
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor profile not found"
        )

    # Generate slug
    base_slug = data.name.lower().replace(" ", "-")
    slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"

    # SECURITY: Prevent mass assignment
    property_data_filtered = {
        k: v
        for k, v in data.model_dump().items()
        if k in ALLOWED_FIELDS and k != "slug"
    }

    property_obj = Property(vendor_id=vendor.id, slug=slug, **property_data_filtered)
    db.add(property_obj)
    await db.flush()
    await db.commit()

    # Refresh with eager-loaded relationships for the response
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.rooms),
            selectinload(Property.vendor),
            selectinload(Property.reviews),
        )
        .where(Property.id == property_obj.id)
    )
    property_obj = result.scalar_one()

    # Invalidate property list cache
    await cache.invalidate_tag("properties")

    return PropertyResponse.model_validate(property_obj)


@router.put(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Update property",
    description="Updates a property. Only the owning vendor or SUPER_ADMIN can update.",
)
@limiter.limit("10/minute")
async def update_property(
    request: Request,
    property_id: uuid.UUID,
    data: PropertyUpdate,
    current_user: User = Depends(require_permission("properties", "update")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Property)
        .options(
            selectinload(Property.rooms),
            selectinload(Property.vendor),
            selectinload(Property.reviews),
        )
        .where(Property.id == property_id)
    )
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
        )

    # Ownership check
    if current_user.role == UserRole.VENDOR:
        result_vendor = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = result_vendor.scalar_one_or_none()
        if not vendor or property_obj.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this property",
            )

    # SECURITY: Prevent mass assignment
    for field, value in data.model_dump(exclude_unset=True).items():
        if field in ALLOWED_FIELDS:
            setattr(property_obj, field, value)

    await db.flush()
    await db.commit()

    # Invalidate cache for this property and lists
    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")

    # Cache updated property
    response = PropertyResponse.model_validate(property_obj)
    await cache.set(
        f"properties:detail:{property_id}",
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["properties"],
    )
    await cache.set(
        f"properties:slug:{property_obj.slug}",
        response.model_dump(),
        ttl=CACHE_TTL_DETAIL,
        tags=["properties"],
    )

    return response


@router.delete(
    "/{property_id}",
    response_model=dict,
    summary="Delete property (soft)",
    description="Soft-deletes a property by setting is_active=False. Only the owning vendor or SUPER_ADMIN.",
)
async def delete_property(
    property_id: uuid.UUID,
    current_user: User = Depends(require_permission("properties", "delete")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Property).where(Property.id == property_id))
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
        )

    # Ownership check
    if current_user.role == UserRole.VENDOR:
        result_vendor = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = result_vendor.scalar_one_or_none()
        if not vendor or property_obj.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this property",
            )

    property_obj.is_active = False
    await db.flush()
    await db.commit()

    # Invalidate cache for this property and lists
    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")

    return {"message": "Property deleted successfully"}


async def _check_property_ownership(
    property_id: uuid.UUID, current_user: User, db: AsyncSession
) -> Property:
    """Get a property and verify the current user owns it (or is SUPER_ADMIN)."""
    result = await db.execute(select(Property).where(Property.id == property_id))
    property_obj = result.scalar_one_or_none()

    if not property_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Property not found"
        )

    if current_user.role != UserRole.SUPER_ADMIN:
        result_vendor = await db.execute(
            select(Vendor).where(Vendor.user_id == current_user.id)
        )
        vendor = result_vendor.scalar_one_or_none()
        if not vendor or property_obj.vendor_id != vendor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this property",
            )

    return property_obj


@router.post(
    "/{property_id}/images",
    response_model=PropertyResponse,
    summary="Upload property images",
    description="Upload one or more images to a property. Only the owning vendor or SUPER_ADMIN.",
)
@limiter.limit("10/minute")
async def upload_property_images(
    request: Request,
    property_id: uuid.UUID,
    file: UploadFile = File(...),
    is_cover: bool = Form(default=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    property_obj = await _check_property_ownership(property_id, current_user, db)

    validate_file(file)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )
    validate_image_bytes(contents)

    if cloudinary_service.is_configured():
        try:
            result = await upload_to_cloudinary(file, "properties")
            url = result.url
        except CloudinaryError:
            logger.warning("Cloudinary upload failed, falling back to local")
            result = await save_upload_file(file, "properties")
            url = result.url
    else:
        result = await save_upload_file(file, "properties")
        url = result.url

    if is_cover or not property_obj.images:
        property_obj.cover_image = url
        if property_obj.images:
            property_obj.images = [url] + [
                img for img in property_obj.images if img != url
            ]
        else:
            property_obj.images = [url]
    else:
        if not property_obj.images:
            property_obj.images = []
        property_obj.images.append(url)

    await db.flush()
    await db.commit()

    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")

    return PropertyResponse.model_validate(property_obj)


@router.put(
    "/{property_id}/cover",
    response_model=PropertyResponse,
    summary="Set property cover image",
    description="Sets or replaces the cover image URL for a property. Owner or SUPER_ADMIN only.",
)
@limiter.limit("10/minute")
async def set_property_cover(
    request: Request,
    property_id: uuid.UUID,
    image_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    property_obj = await _check_property_ownership(property_id, current_user, db)

    property_obj.cover_image = image_url
    if image_url not in (property_obj.images or []):
        if not property_obj.images:
            property_obj.images = []
        property_obj.images.append(image_url)

    await db.flush()
    await db.commit()

    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")

    return PropertyResponse.model_validate(property_obj)


@router.delete(
    "/{property_id}/images",
    response_model=PropertyResponse,
    summary="Remove property image",
    description="Removes an image from a property's image list. Owner or SUPER_ADMIN only.",
)
async def remove_property_image(
    property_id: uuid.UUID,
    image_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    property_obj = await _check_property_ownership(property_id, current_user, db)

    if property_obj.cover_image == image_url:
        property_obj.cover_image = None

    if property_obj.images and image_url in property_obj.images:
        property_obj.images.remove(image_url)

    await db.flush()
    await db.commit()

    await cache.delete(f"properties:detail:{property_id}")
    await cache.delete(f"properties:slug:{property_obj.slug}")
    await cache.invalidate_tag("properties")

    return PropertyResponse.model_validate(property_obj)
