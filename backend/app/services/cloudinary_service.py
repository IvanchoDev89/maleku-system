"""
Cloudinary Service - Gestiona subida y optimización de imágenes
"""

from typing import Optional, Dict, Any, List

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    cloudinary = None

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CloudinaryError(Exception):
    """Custom Cloudinary error"""

    pass


class CloudinaryService:
    """Service for handling image uploads to Cloudinary"""

    def __init__(self):
        self.configured = False
        if not CLOUDINARY_AVAILABLE:
            logger.warning(
                "Cloudinary not installed. Image uploads will be unavailable."
            )
            return
        if settings.CLOUDINARY_CLOUD_NAME:
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET,
                secure=True,
            )
            self.configured = True

    async def upload_image(
        self,
        file_content: bytes,
        folder: str = "general",
        filename: Optional[str] = None,
        transformation: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Upload an image to Cloudinary.

        Args:
            file_content: Raw bytes of the image
            folder: Cloudinary folder to store the image (e.g., 'properties', 'users', 'tours')
            filename: Optional filename (used for public_id)
            transformation: Optional transformation to apply during upload

        Returns:
            Dict with image URL and metadata
        """
        if not self.configured:
            raise CloudinaryError("Cloudinary not configured")

        try:
            # Build upload options
            upload_options = {
                "folder": f"{settings.CLOUDINARY_FOLDER_PREFIX}/{folder}",
                "resource_type": "image",
                "use_filename": True if filename else False,
                "unique_filename": True,
                "overwrite": False,
            }

            if filename:
                # Create clean public_id from filename
                public_id = filename.rsplit(".", 1)[0]  # Remove extension
                public_id = public_id.replace(" ", "_").replace("-", "_")
                upload_options["public_id"] = public_id

            # Add transformation if specified
            if transformation:
                upload_options["transformation"] = transformation

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(file_content, **upload_options)

            logger.info(f"Image uploaded to Cloudinary: {result['public_id']}")

            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "folder": folder,
            }

        except (
            cloudinary.exceptions.Error,
            cloudinary.exceptions.ApiError,
            ValueError,
        ) as e:
            logger.error(f"Cloudinary upload failed: {e}")
            raise CloudinaryError(f"Upload failed: {str(e)}") from e

    def get_optimized_url(
        self,
        public_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        crop: str = "fill",
        quality: str = "auto",
        format: str = "auto",
    ) -> str:
        """
        Generate an optimized image URL with transformations.

        Args:
            public_id: Cloudinary public ID
            width: Target width
            height: Target height
            crop: Crop mode (fill, fit, limit, etc.)
            quality: Quality setting (auto, good, eco)
            format: Output format (auto, webp, jpg, etc.)

        Returns:
            Optimized URL
        """
        if not self.configured:
            raise CloudinaryError("Cloudinary not configured")

        transformation = {"crop": crop, "quality": quality, "fetch_format": format}

        if width:
            transformation["width"] = width
        if height:
            transformation["height"] = height

        return cloudinary.CloudinaryImage(public_id).build_url(**transformation)

    def get_responsive_url(
        self,
        public_id: str,
        sizes: List[int] = [400, 800, 1200],
        aspect_ratio: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate responsive image URLs for different screen sizes.

        Returns:
            Dict mapping size to URL
        """
        if not self.configured:
            raise CloudinaryError("Cloudinary not configured")

        urls = {}
        for size in sizes:
            transformation = {
                "width": size,
                "quality": "auto",
                "fetch_format": "auto",
                "crop": "fill",
            }

            if aspect_ratio:
                transformation["aspect_ratio"] = aspect_ratio

            urls[f"w{size}"] = cloudinary.CloudinaryImage(public_id).build_url(
                **transformation
            )

        return urls

    async def delete_image(self, public_id: str) -> bool:
        """
        Delete an image from Cloudinary.

        Args:
            public_id: Cloudinary public ID

        Returns:
            True if deleted successfully
        """
        if not self.configured:
            raise CloudinaryError("Cloudinary not configured")

        try:
            result = cloudinary.uploader.destroy(public_id)

            if result.get("result") == "ok":
                logger.info(f"Image deleted from Cloudinary: {public_id}")
                return True
            else:
                logger.warning(f"Failed to delete image: {public_id}")
                return False

        except (cloudinary.exceptions.Error, cloudinary.exceptions.ApiError) as e:
            logger.error(f"Cloudinary delete failed: {e}")
            raise CloudinaryError(f"Delete failed: {str(e)}") from e

    def is_configured(self) -> bool:
        """Check if Cloudinary is properly configured"""
        return self.configured


# Singleton instance
cloudinary_service = CloudinaryService()
