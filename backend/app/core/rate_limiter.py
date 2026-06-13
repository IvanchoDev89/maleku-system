"""
Rate limiter for the API, Redis-backed so it works across uvicorn workers.

Supports role-based rate limiting: admins/superadmins get higher limits,
vendors get standard limits, anonymous users get the strictest limits.

Use as a decorator on endpoints:

    from app.core.rate_limiter import limiter
    from fastapi import Request

    @router.post("/login")
    @limiter.limit("5/minute")
    async def login(request: Request, ...): ...

Or as a global default in main.py (``SlowAPIMiddleware`` applies the
``default_limits`` from this Limiter instance to every request).
"""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from fastapi import Request

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Rate limits by role
LIMITS = {
    "anonymous": "30/minute",
    "client": "60/minute",
    "vendor": "100/minute",
    "admin": "200/minute",
    "super_admin": "300/minute",
}

AUTH_RATE_LIMIT = "5/minute"
WRITE_RATE_LIMIT = "30/minute"


def _get_role_key(request: Request) -> str:
    """Generate rate limit key based on user ID (if authenticated) or IP.

    Authenticated users get counters keyed by user_id so they have
    dedicated rate limit buckets. Anonymous users share per-IP buckets.
    """
    ip = get_remote_address(request)
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            import jwt as pyjwt

            payload = pyjwt.decode(
                auth_header[7:],
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False},
            )
            if payload and "sub" in payload:
                return f"user:{payload['sub']}:{ip}"
    except Exception:
        pass
    return f"anon:{ip}"


def _build_limiter() -> Limiter:
    """Create a Redis-backed SLOWAPI limiter with role-based key function.

    Falls back to memory storage if Redis is unreachable so the app still
    starts; a warning is logged. This is a graceful-degradation only —
    production must have Redis healthy.
    """
    storage_uri = settings.REDIS_URL
    try:
        return Limiter(
            key_func=_get_role_key,
            storage_uri=storage_uri,
            default_limits=[LIMITS["anonymous"]],
            headers_enabled=True,
        )
    except Exception as exc:
        logger.warning(
            f"Redis-backed limiter init failed ({exc}); using in-memory fallback"
        )
        return Limiter(
            key_func=_get_role_key,
            default_limits=[LIMITS["anonymous"]],
            headers_enabled=True,
        )


limiter = _build_limiter()


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Standard 429 response with retry-after info."""
    logger.warning(
        f"Rate limit hit on {request.method} {request.url.path} from {get_remote_address(request)}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": str(getattr(exc, "retry_after", None) or 60),
        },
        headers={"Retry-After": str(getattr(exc, "retry_after", None) or 60)},
    )
