"""
Super Admin Audit & Security Logging endpoints.
Provides access to comprehensive audit trails and security logs.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import require_superadmin, get_current_user
from app.core.utils import escape_like_pattern
from app.core.logging import get_logger
from app.models import User, AuditLog, SecurityLog, AuditAction, SecurityAction

logger = get_logger(__name__)
router = APIRouter()


# Response Models
class AuditLogItem(BaseModel):
    """Audit log entry."""
    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[str]
    entity_name: Optional[str]
    old_values: Optional[dict]
    new_values: Optional[dict]
    changes_summary: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_path: Optional[str]
    created_at: datetime


class SecurityLogItem(BaseModel):
    """Security log entry."""
    id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    description: Optional[str]
    severity: str
    details: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    session_id: Optional[str]
    created_at: datetime


class LogSummary(BaseModel):
    """Summary statistics for logs."""
    total_audit_logs: int
    total_security_logs: int
    today_audit_logs: int
    today_security_logs: int
    failed_logins_24h: int
    critical_events_24h: int


class ClientEventCreate(BaseModel):
    """Client-side event reported by the frontend (route access, etc)."""
    event_type: str = Field(..., max_length=100, description="e.g. superadmin_access_denied")
    path: str = Field(..., max_length=500)
    metadata: Optional[dict] = None
    severity: Optional[str] = Field(None, max_length=20)


# Endpoints

@router.post("/logs", status_code=201)
async def create_client_event(
    event: ClientEventCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a client-side event (e.g. superadmin middleware denying access).

    SECURITY: the event_type is mapped to a known AuditAction enum value to
    avoid storing attacker-controlled data in the ``action`` column. Free-form
    text is captured in ``changes_summary`` and ``extra_data`` instead.
    """
    event_type = event.event_type.lower()
    action = AuditAction.VIEW
    security_action: Optional[SecurityAction] = None
    severity = event.severity or "info"

    if "denied" in event_type or "deny" in event_type:
        security_action = SecurityAction.ACCESS_DENIED
        severity = "warning"
    elif "blocked" in event_type or "suspicious" in event_type:
        security_action = SecurityAction.SUSPICIOUS_ACTIVITY
        severity = "critical"

    client_ip = request.client.host if request.client else None
    if request.headers.get("x-forwarded-for"):
        client_ip = request.headers.get("x-forwarded-for").split(",")[0].strip()

    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action=action,
        entity_type="route",
        entity_name=event_type,
        request_path=event.path,
        request_method="EVENT",
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent", "")[:500],
        changes_summary=f"client_event: {event_type}",
        extra_data=event.metadata or {},
    )
    db.add(audit)

    if security_action is not None:
        security_log = SecurityLog(
            user_id=current_user.id,
            user_email=current_user.email,
            action=security_action,
            description=f"client_event: {event_type}",
            severity=severity,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", "")[:500],
            extra_data=event.metadata or {},
        )
        db.add(security_log)

    await db.commit()
    logger.info(f"Client event recorded: {event_type} from {client_ip} for user {current_user.id}")
    return {"status": "recorded", "event_type": event_type}


@router.get("/logs", response_model=List[AuditLogItem])
async def get_audit_logs(
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    action: Optional[AuditAction] = Query(None, description="Filter by action type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[UUID] = Query(None, description="Filter by specific entity"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    search: Optional[str] = Query(None, max_length=200, description="Search in summary or entity name"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Query audit logs with comprehensive filtering.
    """
    query = select(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    
    if action:
        query = query.where(AuditLog.action == action)
    
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    
    if date_from:
        query = query.where(AuditLog.created_at >= date_from)
    
    if date_to:
        query = query.where(AuditLog.created_at <= date_to)
    
    if search:
        safe_search = escape_like_pattern(search)
        search_filter = f"%{safe_search}%"
        query = query.where(
            or_(
                AuditLog.changes_summary.ilike(search_filter),
                AuditLog.entity_name.ilike(search_filter),
            )
        )
    
    # Order by created_at desc
    query = query.order_by(desc(AuditLog.created_at))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "user_email": log.user_email,
            "action": log.action.value,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "entity_name": log.entity_name,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "changes_summary": log.changes_summary,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "user_agent": log.user_agent,
            "request_path": log.request_path,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/logs/count")
async def get_audit_logs_count(
    user_id: Optional[UUID] = Query(None),
    action: Optional[AuditAction] = Query(None),
    entity_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """Get total count of audit logs with filters."""
    query = select(func.count(AuditLog.id))
    
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if date_from:
        query = query.where(AuditLog.created_at >= date_from)
    if date_to:
        query = query.where(AuditLog.created_at <= date_to)
    
    result = await db.execute(query)
    count = result.scalar() or 0
    
    return {"count": count}


@router.get("/logs/{log_id}", response_model=AuditLogItem)
async def get_audit_log_detail(
    log_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """Get detailed information about a specific audit log entry."""
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    
    return {
        "id": str(log.id),
        "user_id": str(log.user_id) if log.user_id else None,
        "user_email": log.user_email,
        "action": log.action.value,
        "entity_type": log.entity_type,
        "entity_id": str(log.entity_id) if log.entity_id else None,
        "entity_name": log.entity_name,
        "old_values": log.old_values,
        "new_values": log.new_values,
        "changes_summary": log.changes_summary,
        "ip_address": str(log.ip_address) if log.ip_address else None,
        "user_agent": log.user_agent,
        "request_path": log.request_path,
        "created_at": log.created_at,
    }


@router.get("/security", response_model=List[SecurityLogItem])
async def get_security_logs(
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    action: Optional[SecurityAction] = Query(None, description="Filter by action type"),
    severity: Optional[str] = Query(None, max_length=20, description="Filter by severity: info, warning, critical"),
    ip_address: Optional[str] = Query(None, max_length=45, description="Filter by IP address"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Query security logs with comprehensive filtering.
    """
    query = select(SecurityLog)
    
    # Apply filters
    if user_id:
        query = query.where(SecurityLog.user_id == user_id)
    
    if action:
        query = query.where(SecurityLog.action == action)
    
    if severity:
        query = query.where(SecurityLog.severity == severity)
    
    if ip_address:
        query = query.where(SecurityLog.ip_address == ip_address)
    
    if date_from:
        query = query.where(SecurityLog.created_at >= date_from)
    
    if date_to:
        query = query.where(SecurityLog.created_at <= date_to)
    
    # Order by created_at desc
    query = query.order_by(desc(SecurityLog.created_at))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "user_email": log.user_email,
            "action": log.action.value,
            "description": log.description,
            "severity": log.severity,
            "details": log.details,
            "ip_address": str(log.ip_address) if log.ip_address else None,
            "user_agent": log.user_agent,
            "session_id": log.session_id,
            "created_at": log.created_at,
        }
        for log in logs
    ]


@router.get("/security/failed-logins")
async def get_failed_login_attempts(
    hours: int = Query(24, ge=1, le=168, description="Look back period in hours"),
    group_by_ip: bool = Query(False, description="Group results by IP address"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Get failed login attempts for security monitoring.
    Useful for detecting brute force attacks.
    """
    from_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    if group_by_ip:
        # Group by IP to find suspicious patterns
        result = await db.execute(
            select(
                SecurityLog.ip_address,
                func.count(SecurityLog.id).label("attempt_count"),
                func.array_agg(SecurityLog.user_email).label("emails_attempted"),
                func.max(SecurityLog.created_at).label("last_attempt"),
            )
            .where(SecurityLog.action == SecurityAction.LOGIN_FAILURE)
            .where(SecurityLog.created_at >= from_time)
            .group_by(SecurityLog.ip_address)
            .having(func.count(SecurityLog.id) >= 3)  # Only show IPs with 3+ failures
            .order_by(desc("attempt_count"))
        )
        
        return [
            {
                "ip_address": str(row.ip_address) if row.ip_address else None,
                "attempt_count": row.attempt_count,
                "emails_attempted": list(set(row.emails_attempted)) if row.emails_attempted else [],
                "last_attempt": row.last_attempt,
            }
            for row in result.all()
        ]
    else:
        # List individual failed attempts
        result = await db.execute(
            select(SecurityLog)
            .where(SecurityLog.action == SecurityAction.LOGIN_FAILURE)
            .where(SecurityLog.created_at >= from_time)
            .order_by(desc(SecurityLog.created_at))
            .limit(100)
        )
        
        logs = result.scalars().all()
        return [
            {
                "id": str(log.id),
                "user_email": log.user_email,
                "ip_address": str(log.ip_address) if log.ip_address else None,
                "user_agent": log.user_agent,
                "details": log.details,
                "created_at": log.created_at,
            }
            for log in logs
        ]


@router.get("/summary", response_model=LogSummary)
async def get_logs_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Get summary statistics for audit and security logs.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_ago = now - timedelta(hours=24)
    
    # Total counts
    total_audit_result = await db.execute(select(func.count(AuditLog.id)))
    total_audit = total_audit_result.scalar() or 0
    
    total_security_result = await db.execute(select(func.count(SecurityLog.id)))
    total_security = total_security_result.scalar() or 0
    
    # Today's counts
    today_audit_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= today_start)
    )
    today_audit = today_audit_result.scalar() or 0
    
    today_security_result = await db.execute(
        select(func.count(SecurityLog.id)).where(SecurityLog.created_at >= today_start)
    )
    today_security = today_security_result.scalar() or 0
    
    # Failed logins in last 24h
    failed_logins_result = await db.execute(
        select(func.count(SecurityLog.id))
        .where(SecurityLog.action == SecurityAction.LOGIN_FAILURE)
        .where(SecurityLog.created_at >= day_ago)
    )
    failed_logins = failed_logins_result.scalar() or 0
    
    # Critical events in last 24h
    critical_events_result = await db.execute(
        select(func.count(SecurityLog.id))
        .where(SecurityLog.severity == "critical")
        .where(SecurityLog.created_at >= day_ago)
    )
    critical_events = critical_events_result.scalar() or 0
    
    return {
        "total_audit_logs": total_audit,
        "total_security_logs": total_security,
        "today_audit_logs": today_audit,
        "today_security_logs": today_security,
        "failed_logins_24h": failed_logins,
        "critical_events_24h": critical_events,
    }


@router.post("/export")
async def export_logs(
    log_type: str = Query(..., description="Type of logs: 'audit' or 'security'"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    format: str = Query("json", description="Export format: json, csv"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin())
):
    """
    Export logs for external analysis or compliance.
    """
    # Log this export action
    from app.services.audit_service import AuditService
    await AuditService.log_action(
        db=db,
        user=current_user,
        action=AuditAction.EXPORT,
        entity_type="logs",
        entity_id=None,
        entity_name=f"{log_type}_logs",
        changes_summary=f"Exported {log_type} logs from {date_from} to {date_to}",
        metadata={"format": format, "date_from": date_from.isoformat() if date_from else None, "date_to": date_to.isoformat() if date_to else None},
    )
    await db.commit()
    
    # This is a placeholder - actual implementation would generate file
    return {
        "message": f"Export of {log_type} logs initiated",
        "format": format,
        "status": "processing",
        "download_url": f"/api/v1/superadmin/audit/export/download?type={log_type}&format={format}",
    }
