from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import init_db
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.api.v1.endpoints import auth
from app.api.v1 import users, vendors, properties, tours, bookings, blog, destinations
try:
    from app.api.v1.landing import router as landing_router
    print("Landing router imported successfully")
except Exception as e:
    print(f"Failed to import landing router: {e}")
    landing_router = None
from app.api.v1.analytics import router as analytics_router
from app.api.v1.admin.settings import router as settings_router
from app.api.v1.admin.vendors import router as admin_vendors_router
from app.api.v1.vehicles import router as vehicles_router
from app.api.v1.boats import router as boats_router
from app.api.v1.flights import router as flights_router
from app.api.v1.transportation import router as transportation_router
from app.api.v1.pricing import router as pricing_router
from app.api.v1.chat import router as chat_router
from app.api.v1.search import router as search_router
from app.api.v1.upload import router as upload_router
from app.api.v1.availability import router as availability_router
from app.api.v1.stripe import router as stripe_router
from app.api.v1.marketing import router as marketing_router
from app.api.v1.newsletter import router as newsletter_router
from app.api.v1.superadmin import router as superadmin_router
from app.core.logging import setup_logging, get_logger
from app.middleware.error_handler import ErrorHandlerMiddleware

# Setup Sentry monitoring
if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1,
        send_default_pii=False
    )

# Setup logging
setup_logging(level="INFO", json_format=False)
logger = get_logger(__name__)

# Rate limiter (Redis-backed, configured in app.core.rate_limiter)
from app.core.rate_limiter import limiter  # noqa: F401

# Global rate limits
DEFAULT_RATE_LIMIT = "100/minute"
AUTH_RATE_LIMIT = "5/minute"
WRITE_RATE_LIMIT = "30/minute"

@asynccontextmanager
async def _lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Costa Rica Travel - Multi-vendor Tourism Marketplace API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    terms_of_service="https://costaricatravel.dev/terms",
    contact={
        "name": "Costa Rica Travel",
        "url": "https://costaricatravel.dev/contact"
    },
    lifespan=_lifespan,
)

# CORS - MUST be first middleware to handle preflight OPTIONS requests
cors_origins = settings.cors_origins_list

# En desarrollo, usar whitelist específica en lugar de wildcard
# Esto previene que DEBUG=True accidentalmente exponga CORS abierto en producción
if settings.DEBUG or settings.ENVIRONMENT == "development":
    cors_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "http://localhost:4173",  # Vite preview
        "http://127.0.0.1:4173",
        "http://127.0.0.1:45975",  # Windsurf browser preview
        "http://localhost:45975",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Origin", "Content-Type", "Accept", "Authorization", "X-Request-ID", "X-Requested-With"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Security: Rate limiting (Redis-backed, applied per-endpoint via @limiter.limit)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Security: Global error handler (prevents info leakage)
app.add_middleware(ErrorHandlerMiddleware)

# Security: Trusted hosts (prevent host header attacks)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "costaricatravel.dev",
        "www.costaricatravel.dev",
        "app.costaricatravel.dev",
        "api.costaricatravel.dev",
        "admin.costaricatravel.dev",
        "*.costaricatravel.dev",
    ]
)

# Security: Custom security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Content Security Policy (CSP)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    return response


# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    from time import time
    
    start_time = time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time() - start_time) * 1000
    
    # Log request (skip health checks to reduce noise)
    if request.url.path not in ["/health", "/health/ready", "/health/live"]:
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms)",
            extra={
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2)
                }
            }
        )
    
    return response

# Exception handlers (SLOWAPI uses the handler registered in app.core.rate_limiter)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "exception": str(exc),
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# Router with rate limiting
api_v1 = "/api/v1"

# Authentication routes
app.include_router(
    auth.router, 
    prefix=f"{api_v1}/auth", 
    tags=["Authentication"]
)

# Admin routes
app.include_router(
    analytics_router, 
    prefix=f"{api_v1}/admin/analytics", 
    tags=["Admin Analytics"]
)
app.include_router(
    settings_router, 
    prefix=f"{api_v1}/admin/settings", 
    tags=["Admin Settings"]
)
app.include_router(
    admin_vendors_router, 
    prefix=f"{api_v1}/admin/vendors", 
    tags=["Admin Vendors"]
)

# Super Admin routes (exclusive access for SUPER_ADMIN)
app.include_router(
    superadmin_router,
    prefix=f"{api_v1}/superadmin",
    tags=["Super Admin"]
)

# Standard routes - default rate limit
app.include_router(users.router, prefix=f"{api_v1}/users", tags=["Users"])
app.include_router(vendors.router, prefix=f"{api_v1}/vendors", tags=["Vendors"])
app.include_router(properties.router, prefix=f"{api_v1}/properties", tags=["Properties"])
app.include_router(tours.router, prefix=f"{api_v1}/tours", tags=["Tours"])
app.include_router(bookings.router, prefix=f"{api_v1}/bookings", tags=["Bookings"])
app.include_router(blog.router, prefix=f"{api_v1}/blog", tags=["Blog"])
app.include_router(destinations.router, prefix=f"{api_v1}/destinations", tags=["Destinations"])
app.include_router(landing_router, prefix=f"{api_v1}/landing", tags=["Landing"])
app.include_router(search_router, prefix=f"{api_v1}/search", tags=["Search"])

# Marketplace services
app.include_router(vehicles_router, prefix=f"{api_v1}/vehicles", tags=["Vehicles"])
app.include_router(boats_router, prefix=f"{api_v1}/boats", tags=["Boats"])
app.include_router(flights_router, prefix=f"{api_v1}/flights", tags=["Flights"])
app.include_router(transportation_router, prefix=f"{api_v1}/transportation", tags=["Transportation"])
app.include_router(pricing_router, prefix=f"{api_v1}/pricing", tags=["Pricing"])
app.include_router(chat_router, prefix=f"{api_v1}/chat", tags=["Chat"])
app.include_router(upload_router, prefix=f"{api_v1}/upload", tags=["Upload"])
app.include_router(availability_router, prefix=f"{api_v1}/availability", tags=["Availability"])
app.include_router(stripe_router, prefix=f"{api_v1}/stripe", tags=["Stripe Payments"])
app.include_router(newsletter_router, prefix=f"{api_v1}/newsletter", tags=["Newsletter"])

# Marketing routes (BillionMail integration)
app.include_router(marketing_router, prefix=f"{api_v1}/marketing", tags=["Marketing"])

# API Health check endpoint for frontend
@app.get(f"{api_v1}/health")
async def api_health_check():
    """Health check endpoint at API level for frontend monitoring"""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

# Static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Basic health check - returns 200 if service is running"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.get("/health/ready")
async def health_ready():
    """Readiness check - verifies database connection"""
    from app.core.database import engine
    from sqlalchemy import text

    db_status = "unknown"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except (OSError, RuntimeError) as e:
        # SECURITY: do not leak internal error details to client (OWASP API8)
        # Full error is logged server-side; client gets a generic status
        logger.error(f"Database readiness check failed: {e}")
        db_status = "unavailable"

    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health/live")
async def health_live():
    """Liveness check - verifies process is running"""
    import os
    return {
        "status": "alive",
        "pid": os.getpid()
    }