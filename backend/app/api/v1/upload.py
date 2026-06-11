import asyncio
import io
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from pydantic import BaseModel
import re
from PIL import Image, UnidentifiedImageError

from app.core.logging import get_logger
from app.core.security import get_current_user, require_role
from app.models import User, UserRole
from app.services.cloudinary_service import cloudinary_service, CloudinaryError

logger = get_logger(__name__)

router = APIRouter(tags=["Upload"])

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp'
}
_ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "WEBP"}
ALLOWED_FOLDERS = {'general', 'properties', 'tours', 'users', 'gallery', 'blog', 'destinations', 'avatars'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

UPLOAD_DIR = Path("uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class UploadResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    url: str
    size: int
    content_type: str
    provider: str = "local"
    public_id: Optional[str] = None
    responsive_urls: Optional[dict] = None


class DeleteResponse(BaseModel):
    success: bool
    message: str
    provider: str = "local"


def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Content type not allowed. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )


def validate_image_bytes(contents: bytes) -> None:
    """SECURITY: verify the file is a real image by parsing its magic bytes.

    Prevents attackers from uploading polyglot files (e.g. a PHP script
    renamed to .jpg) since extension and Content-Type are client-controlled.
    """
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()
        # Re-open to access the .format attribute (verify() closes the image)
        img = Image.open(io.BytesIO(contents))
        if img.format not in _ALLOWED_IMAGE_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Image format not allowed: {img.format}",
            )
    except (UnidentifiedImageError, OSError, ValueError) as e:
        logger.warning(f"Image magic-bytes validation failed: {e}")
        raise HTTPException(
            status_code=400,
            detail="File is not a valid image",
        )


def validate_folder(folder: str) -> str:
    folder = folder.strip().lower()
    folder = re.sub(r'[^a-z0-9_-]', '', folder)
    if not folder or folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder. Allowed: {', '.join(sorted(ALLOWED_FOLDERS))}"
        )
    return folder


def sanitize_path(path: str) -> Path:
    path = path.replace('\x00', '')
    safe_path = Path(path).resolve()
    upload_base = UPLOAD_DIR.resolve()
    try:
        safe_path.relative_to(upload_base)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid path: path traversal detected"
        )
    return safe_path


async def save_upload_file(file: UploadFile, folder: str) -> UploadResponse:
    validate_file(file)
    folder = validate_folder(folder)

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    # SECURITY: verify magic bytes match the claimed image type
    validate_image_bytes(contents)

    ext = Path(file.filename).suffix.lower()
    unique_id = uuid.uuid4().hex
    unique_filename = f"{unique_id}{ext}"

    date_path = Path(folder) / datetime.now(timezone.utc).strftime("%Y/%m/%d")
    target_dir = UPLOAD_DIR / date_path
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / unique_filename
    safe_path = sanitize_path(str(file_path))

    async with aiofiles.open(safe_path, 'wb') as f:
        await f.write(contents)

    url_path = f"/uploads/{date_path}/{unique_filename}"

    return UploadResponse(
        id=unique_id,
        filename=unique_filename,
        original_filename=file.filename or "unnamed",
        url=url_path,
        size=len(contents),
        content_type=file.content_type or 'image/jpeg'
    )


async def upload_to_cloudinary(file: UploadFile, folder: str) -> UploadResponse:
    folder = validate_folder(folder)
    contents = await file.read()

    # SECURITY: verify magic bytes match the claimed image type
    validate_image_bytes(contents)

    ext = Path(file.filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:16]
    unique_filename = f"{folder}_{unique_id}{ext}"

    result = await cloudinary_service.upload_image(
        file_content=contents,
        folder=folder,
        filename=unique_filename
    )

    responsive_urls = cloudinary_service.get_responsive_url(
        public_id=result["public_id"],
        sizes=[400, 800, 1200]
    )

    return UploadResponse(
        id=unique_id,
        filename=unique_filename,
        original_filename=file.filename or "unnamed",
        url=result["url"],
        size=result["bytes"],
        content_type=file.content_type or 'image/jpeg',
        provider="cloudinary",
        public_id=result["public_id"],
        responsive_urls=responsive_urls
    )


@router.post("/image", response_model=UploadResponse,
             summary="Upload single image",
             description="Uploads a single image file (JPG, PNG, GIF, WebP). Max 10MB. Validates MIME type and image integrity.")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Form(default="general"),
    use_cloudinary: bool = Form(default=True),
    current_user: User = Depends(get_current_user)
):
    if use_cloudinary and cloudinary_service.is_configured():
        try:
            logger.info(f"Uploading to Cloudinary: {file.filename} to folder: {folder}")
            return await upload_to_cloudinary(file, folder)
        except CloudinaryError as e:
            logger.warning(f"Cloudinary upload failed, falling back to local: {e}")

    logger.info(f"Uploading locally: {file.filename} to folder: {folder}")
    return await save_upload_file(file, folder)


@router.post("/images", response_model=List[UploadResponse],
             summary="Upload multiple images",
             description="Uploads up to 10 images in parallel. Each file is validated and saved independently. Max total: 10 files.")
async def upload_images(
    files: List[UploadFile] = File(...),
    folder: str = Form(default="gallery"),
    current_user: User = Depends(get_current_user)
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed at once")

    folder = validate_folder(folder)

    async def _upload_one(file: UploadFile) -> UploadResponse:
        try:
            return await save_upload_file(file, folder)
        except HTTPException:
            raise

    results = await asyncio.gather(*[_upload_one(f) for f in files])

    return list(results)


@router.delete("/image/{file_id}", response_model=dict,
               summary="Delete image",
               description="Deletes an image from Cloudinary (if provider=cloudinary with public_id) or from local storage. ADMIN/SUPER_ADMIN role required.")
async def delete_image(
    file_id: str,
    path: str,
    public_id: Optional[str] = None,
    provider: str = "local",
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.SUPER_ADMIN))
):
    try:
        if provider == "cloudinary" and public_id:
            success = await cloudinary_service.delete_image(public_id)
            return DeleteResponse(
                success=success,
                message="Image deleted from Cloudinary" if success else "Failed to delete from Cloudinary",
                provider="cloudinary"
            )
        else:
            file_path = sanitize_path(path)
            if file_path.exists():
                file_path.unlink()
                return DeleteResponse(
                    success=True,
                    message="Image deleted successfully",
                    provider="local"
                )
            return DeleteResponse(
                success=False,
                message="Image not found",
                provider="local"
            )
    except (OSError, RuntimeError) as e:
        logger.error(f"Error deleting image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image. Please try again later.") from e


@router.get("/presigned-url", response_model=dict,
            summary="Get presigned upload URL",
            description="Returns upload URL and metadata for a client-side upload. Validates file extension against allowed types.")
async def get_presigned_url(
    filename: str,
    folder: str = "general",
    current_user: User = Depends(get_current_user)
):
    folder = validate_folder(folder)
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    filename = f"{uuid.uuid4().hex}{ext}"

    return {
        "upload_url": "/api/v1/upload/image",
        "fields": {"folder": folder},
        "key": f"{folder}/{filename}",
        "expires_in": 3600
    }
