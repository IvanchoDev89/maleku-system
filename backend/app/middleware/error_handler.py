"""Global error handling middleware with security-focused responses."""

import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

IS_DEV = settings.ENVIRONMENT == "development"


def _error_content(exc: Exception, generic_msg: str) -> dict:
    """Return error detail; never include traceback in response body."""
    content: dict = {"detail": generic_msg}
    return content


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Centralized error handling with security considerations."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception):
        """Handle different exception types with appropriate responses."""

        # SQLAlchemy errors - don't leak DB details
        if isinstance(exc, (SQLAlchemyError, IntegrityError)):
            logger.error(f"Database error: {str(exc)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=_error_content(
                    exc, "A database error occurred. Please try again later."
                ),
            )

        # Validation errors — preserve detail
        if hasattr(exc, "status_code") and exc.status_code == 422:
            detail = getattr(
                exc, "detail", "Invalid input data. Please check your request."
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": detail},
            )

        # HTTP exceptions - pass through but sanitize
        if hasattr(exc, "status_code"):
            if exc.status_code >= 500:
                logger.error(f"Server error: {str(exc)}\n{traceback.format_exc()}")
                return JSONResponse(
                    status_code=exc.status_code,
                    content=_error_content(exc, "An internal server error occurred."),
                )

            # Client errors - safe to return detail
            detail = getattr(exc, "detail", str(exc))
            return JSONResponse(status_code=exc.status_code, content={"detail": detail})

        # Unknown exceptions - log full traceback, return generic error
        logger.critical(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_content(
                exc, "An unexpected error occurred. Our team has been notified."
            ),
        )
