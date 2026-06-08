"""
Rate limiter for the API, Redis-backed so it works across uvicorn workers.

The previous in-memory middleware (``app.middleware.rate_limit``) was process-local
and silently disabled in any multi-worker deployment. SLOWAPI is wired here with
``limits.aio.storage.RedisStorage`` pointing at the same Redis we use for caching.

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


def _build_limiter() -> Limiter:
    """Create a Redis-backed SLOWAPI limiter.

    Falls back to memory storage if Redis is unreachable so the app still
    starts; a warning is logged. This is a graceful-degradation only —
    production must have Redis healthy.
    """
    storage_uri = settings.REDIS_URL
    try:
        return Limiter(
            key_func=get_remote_address,
            storage_uri=storage_uri,
            default_limits=["100/minute"],
            headers_enabled=True,
        )
    except Exception as exc:
        logger.warning(f"Redis-backed limiter init failed ({exc}); using in-memory fallback")
        return Limiter(
            key_func=get_remote_address,
            default_limits=["100/minute"],
            headers_enabled=True,
        )


limiter = _build_limiter()


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Standard 429 response with retry-after info."""
    logger.warning(f"Rate limit hit on {request.method} {request.url.path} from {get_remote_address(request)}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": str(getattr(exc, "retry_after", None) or 60),
        },
        headers={"Retry-After": str(getattr(exc, "retry_after", None) or 60)},
    )
