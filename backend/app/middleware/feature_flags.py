from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.feature_flags import is_enabled, FeatureFlag


class FeatureFlagMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_enabled(FeatureFlag.MAINTENANCE_MODE):
            if not request.url.path.startswith(
                ("/health", "/docs", "/redoc", "/metrics")
            ):
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": "Service unavailable due to maintenance. Please try again later."
                    },
                )
        return await call_next(request)
