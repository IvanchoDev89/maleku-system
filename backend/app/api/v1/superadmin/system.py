"""
Super Admin System & Infrastructure endpoints.
Provides health checks, database stats, and system monitoring.
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.models import User

router = APIRouter(tags=["SuperAdmin - System"])


# Response Models
class SystemHealth(BaseModel):
    """System health status."""

    status: str
    api_status: str
    database_status: str
    timestamp: datetime
    uptime_seconds: int | None
    version: str


class DatabaseStats(BaseModel):
    """Database statistics."""

    total_size_mb: float
    tables: list
    connection_count: int
    slow_queries: list


class CacheStats(BaseModel):
    """Cache statistics."""

    type: str
    status: str
    hits: int
    misses: int
    hit_rate: float
    memory_usage_mb: float
    keys_count: int


class QueueStats(BaseModel):
    """Queue/worker statistics."""

    queued_jobs: int
    processing_jobs: int
    failed_jobs: int
    completed_jobs_24h: int
    workers_active: int


class BackupInfo(BaseModel):
    """Backup information."""

    id: str
    type: str
    status: str
    size_mb: float
    created_at: datetime
    completed_at: datetime | None


# Endpoints
@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get overall system health status.
    """
    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except (OSError, RuntimeError):
        db_status = "error"

    # Overall status
    if db_status == "connected":
        overall_status = "healthy"
    else:
        overall_status = "degraded"

    return {
        "status": overall_status,
        "api_status": "operational",
        "database_status": db_status,
        "timestamp": datetime.now(UTC),
        "uptime_seconds": None,  # Would need to track application start time
        "version": "1.0.0",  # Should come from app config
    }


@router.get("/database/stats", response_model=dict)
async def get_database_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get database statistics including size and table information.
    """
    # Get database size
    size_result = await db.execute(
        text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                   pg_database_size(current_database()) as size_bytes
        """)
    )
    size_row = size_result.fetchone()

    # Get table statistics
    tables_result = await db.execute(
        text("""
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                n_live_tup as row_count
            FROM pg_stat_user_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
    )
    tables = [
        {
            "schema": row.schemaname,
            "name": row.tablename,
            "size": row.size,
            "size_bytes": row.size_bytes,
            "row_count": row.row_count,
        }
        for row in tables_result.fetchall()
    ]

    # Get connection count
    connections_result = await db.execute(text("SELECT count(*) as count FROM pg_stat_activity"))
    connections = connections_result.scalar() or 0

    return {
        "total_size": size_row.size if size_row else "unknown",
        "total_size_bytes": size_row.size_bytes if size_row else 0,
        "total_size_mb": round((size_row.size_bytes / (1024 * 1024)), 2) if size_row else 0,
        "tables": tables,
        "connection_count": connections,
        "slow_queries": [],  # Would need to track query performance
    }


@router.get("/database/connections", response_model=dict)
async def get_database_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get active database connections.
    """
    result = await db.execute(
        text("""
            SELECT
                pid,
                usename as username,
                application_name,
                client_addr as client_address,
                backend_start,
                state,
                query_start,
                query
            FROM pg_stat_activity
            WHERE datname = current_database()
            ORDER BY backend_start DESC
        """)
    )

    connections = []
    for row in result.fetchall():
        connections.append(
            {
                "pid": row.pid,
                "username": row.username,
                "application": row.application_name,
                "client_address": str(row.client_address) if row.client_address else None,
                "backend_start": row.backend_start,
                "state": row.state,
                "query_start": row.query_start,
                "query": row.query[:200] if row.query else None,  # Truncate long queries
            }
        )

    return {
        "count": len(connections),
        "connections": connections,
    }


@router.get("/cache/stats", response_model=dict)
async def get_cache_stats(current_user: User = Depends(require_superadmin())):
    """
    Get cache statistics.
    Placeholder - would integrate with actual cache (Redis/Memcached).
    """
    # This is a placeholder - actual implementation would connect to Redis/Memcached
    return {
        "type": "redis",  # or "memcached"
        "status": "not_configured",
        "hits": 0,
        "misses": 0,
        "hit_rate": 0.0,
        "memory_usage_mb": 0.0,
        "keys_count": 0,
        "note": "Cache monitoring not yet configured. Configure Redis to see actual stats.",
    }


@router.get("/queue/stats", response_model=dict)
async def get_queue_stats(current_user: User = Depends(require_superadmin())):
    """
    Get background job queue statistics.
    Placeholder - would integrate with actual queue system (Celery/RQ).
    """
    # This is a placeholder - actual implementation would connect to Celery/RQ
    return {
        "type": "celery",  # or "rq"
        "status": "not_configured",
        "queued_jobs": 0,
        "processing_jobs": 0,
        "failed_jobs": 0,
        "completed_jobs_24h": 0,
        "workers_active": 0,
        "note": "Queue monitoring not yet configured. Configure Celery to see actual stats.",
    }


@router.get("/backups", response_model=dict)
async def get_backups(current_user: User = Depends(require_superadmin())):
    """
    List available backups.
    Placeholder - would integrate with actual backup system.
    """
    # This is a placeholder - actual implementation would list backup files
    return {
        "backups": [],
        "automated_backups_enabled": False,
        "last_backup": None,
        "note": "Automated backups not yet configured. Configure AWS S3 or similar for backups.",
    }


@router.post("/backups/trigger", response_model=dict)
@limiter.limit("5/minute")
async def trigger_backup(request: Request, current_user: User = Depends(require_superadmin())):
    """
    Manually trigger a database backup.
    Placeholder - would integrate with actual backup system.
    """
    # This is a placeholder - actual implementation would trigger pg_dump or similar
    return {
        "message": "Backup initiated",
        "backup_id": "manual-" + datetime.now(UTC).strftime("%Y%m%d-%H%M%S"),
        "status": "processing",
        "note": "Backup system not yet fully configured. This is a placeholder.",
    }


@router.get("/metrics", response_model=dict)
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
):
    """
    Get key system metrics for monitoring dashboards.
    """
    now = datetime.now(UTC)
    day_ago = now - timedelta(hours=24)

    # User metrics
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar() or 0

    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= day_ago)
    )
    new_users_24h = new_users_result.scalar() or 0

    # Active users (logged in within 24h)
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.last_login >= day_ago)
    )
    active_users_24h = active_users_result.scalar() or 0

    # DB connection count
    connections_count = await _get_db_connection_count(db)

    return {
        "timestamp": now,
        "users": {
            "total": total_users,
            "new_24h": new_users_24h,
            "active_24h": active_users_24h,
        },
        "api": {
            "requests_24h": None,
            "average_response_time_ms": None,
            "error_rate": None,
            "prometheus_endpoint": "/metrics",
        },
        "database": {
            "connections": connections_count,
            "slow_queries_24h": None,
        },
        "note": "Real-time request metrics available via GET /metrics (Prometheus format).",
    }


async def _get_db_connection_count(db: AsyncSession) -> int | None:
    """Query active database connection count."""
    try:
        result = await db.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
        )
        return result.scalar() or 0
    except Exception:
        return 0


@router.post("/maintenance-mode", response_model=dict)
@limiter.limit("5/minute")
async def toggle_maintenance_mode(
    request: Request,
    enabled: bool,
    message: str | None = None,
    current_user: User = Depends(require_superadmin()),
):
    """
    Enable or disable maintenance mode.
    When enabled, non-admin users see a maintenance page.
    """
    # This is a placeholder - actual implementation would update a config or cache
    status = "enabled" if enabled else "disabled"

    return {
        "maintenance_mode": enabled,
        "status": status,
        "message": message or ("Site is under maintenance" if enabled else None),
        "affected_routes": "all non-admin endpoints" if enabled else None,
        "note": "Maintenance mode control not yet fully implemented. This is a placeholder.",
    }


@router.get("/environment", response_model=dict)
async def get_environment_info(current_user: User = Depends(require_superadmin())):
    """
    Get environment and configuration information.
    Shows non-sensitive configuration values.
    """
    from app.core.config import settings

    return {
        "environment": settings.ENVIRONMENT if hasattr(settings, "ENVIRONMENT") else "unknown",
        "debug_mode": settings.DEBUG if hasattr(settings, "DEBUG") else False,
        "database_url_masked": settings.DATABASE_URL.replace(
            settings.DATABASE_URL.split("://")[1].split(":")[0], "***"
        )
        if hasattr(settings, "DATABASE_URL")
        else None,
        "features": {
            "email_enabled": bool(settings.SENDGRID_API_KEY)
            if hasattr(settings, "SENDGRID_API_KEY")
            else False,
            "stripe_enabled": bool(settings.STRIPE_SECRET_KEY)
            if hasattr(settings, "STRIPE_SECRET_KEY")
            else False,
            "aws_enabled": bool(settings.AWS_ACCESS_KEY_ID)
            if hasattr(settings, "AWS_ACCESS_KEY_ID")
            else False,
        },
        "security": {
            "token_expiry_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
            if hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")
            else 30,
            "refresh_token_expiry_days": settings.REFRESH_TOKEN_EXPIRE_DAYS
            if hasattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS")
            else 7,
        },
        "note": "Sensitive values are masked. Full configuration requires server access.",
    }
