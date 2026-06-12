"""
Audit service for comprehensive logging of system actions.
Provides methods to log audit events and security events consistently.
"""
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from uuid import UUID
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import AuditLog, SecurityLog, AuditAction, SecurityAction, User


class AuditService:
    """Service for creating and managing audit logs."""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user: Optional[User],
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        entity_name: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        request: Optional[Request] = None,
        changes_summary: Optional[str] = None,
        extra_data: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an audit action.
        
        Args:
            db: Database session
            user: User performing the action (None for anonymous)
            action: Type of action performed
            entity_type: Type of entity affected (e.g., 'user', 'vendor', 'booking')
            entity_id: ID of the affected entity
            entity_name: Human-readable name of the entity
            old_values: Previous state of the entity (for updates)
            new_values: New state of the entity (for creates/updates)
            request: FastAPI request object (to extract IP, user agent)
            changes_summary: Human-readable summary of what changed
            extra_data: Additional flexible metadata
            ip_address: Override IP address (if not from request)
            user_agent: Override user agent (if not from request)
        
        Returns:
            Created AuditLog instance
        """
        # Extract request info if provided
        request_info = AuditService._extract_request_info(request) if request else {}
        
        # Sanitize sensitive data before logging
        old_values = AuditService._sanitize_sensitive_data(old_values)
        new_values = AuditService._sanitize_sensitive_data(new_values)
        
        audit_log = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            old_values=old_values,
            new_values=new_values,
            changes_summary=changes_summary,
            ip_address=ip_address or request_info.get("ip_address"),
            user_agent=user_agent or request_info.get("user_agent"),
            request_method=request_info.get("method"),
            request_path=request_info.get("path"),
            request_id=request_info.get("request_id"),
            session_id=request_info.get("session_id"),
            correlation_id=request_info.get("correlation_id"),
            extra_data=extra_data,
            created_at=datetime.now(timezone.utc),
        )
        
        db.add(audit_log)
        await db.flush()  # Flush to get the ID, but don't commit yet
        
        return audit_log
    
    @staticmethod
    async def log_security_event(
        db: AsyncSession,
        action: SecurityAction,
        user: Optional[User] = None,
        user_email: Optional[str] = None,
        description: Optional[str] = None,
        severity: str = "info",
        details: Optional[Dict] = None,
        request: Optional[Request] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> SecurityLog:
        """
        Log a security-related event.
        
        Args:
            db: Database session
            action: Type of security action
            user: User involved (if known)
            user_email: Email used (for failed login attempts)
            description: Human-readable description
            severity: info, warning, or critical
            details: Additional security context
            request: FastAPI request object
            ip_address: Override IP address
            user_agent: Override user agent
            session_id: Session identifier
        
        Returns:
            Created SecurityLog instance
        """
        request_info = AuditService._extract_request_info(request) if request else {}
        
        # Sanitize sensitive data
        details = AuditService._sanitize_sensitive_data(details)
        
        security_log = SecurityLog(
            user_id=user.id if user else None,
            user_email=user_email or (user.email if user else None),
            action=action,
            description=description,
            severity=severity,
            details=details,
            ip_address=ip_address or request_info.get("ip_address"),
            user_agent=user_agent or request_info.get("user_agent"),
            session_id=session_id or request_info.get("session_id"),
            request_id=request_info.get("request_id"),
            correlation_id=request_info.get("correlation_id"),
            created_at=datetime.now(timezone.utc),
        )
        
        db.add(security_log)
        await db.flush()
        
        return security_log
    
    @staticmethod
    def _extract_request_info(request: Optional[Request]) -> Dict[str, Any]:
        """Extract relevant information from a FastAPI request."""
        if not request:
            return {}
        
        info = {
            "method": request.method,
            "path": str(request.url.path),
        }
        
        # Extract headers
        headers = request.headers
        
        # IP Address handling (handles proxies)
        forwarded_for = headers.get("x-forwarded-for")
        if forwarded_for:
            # Get the first IP in the chain (client IP)
            info["ip_address"] = forwarded_for.split(",")[0].strip()
        else:
            real_ip = headers.get("x-real-ip")
            if real_ip:
                info["ip_address"] = real_ip
            elif hasattr(request.client, 'host'):
                info["ip_address"] = request.client.host
        
        # User agent
        info["user_agent"] = headers.get("user-agent")
        
        # Request/Correlation IDs (prefer request.state set by RequestIDMiddleware)
        state_id = getattr(request.state, "request_id", None) if hasattr(request, "state") else None
        info["request_id"] = state_id or headers.get("x-request-id")
        info["correlation_id"] = headers.get("x-correlation-id")
        
        # Session ID (could come from cookie or header)
        info["session_id"] = headers.get("x-session-id")
        
        return info
    
    @staticmethod
    def _sanitize_sensitive_data(data: Optional[Dict]) -> Optional[Dict]:
        """
        Remove or mask sensitive data before logging.
        Never log passwords, tokens, credit card numbers, etc.
        """
        if not data:
            return data
        
        sensitive_fields = {
            'password', 'password_hash', 'token', 'access_token', 'refresh_token',
            'secret', 'api_key', 'credit_card', 'card_number', 'cvv', 'pin',
            'ssn', 'social_security', 'tax_id', 'secret_key', 'private_key'
        }
        
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # Check if field is sensitive
            if any(sensitive in key_lower for sensitive in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = AuditService._sanitize_sensitive_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    AuditService._sanitize_sensitive_data(item) if isinstance(item, dict) else (
                        item.isoformat() if hasattr(item, 'isoformat') else item
                    )
                    for item in value
                ]
            elif isinstance(value, datetime):
                sanitized[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):
                sanitized[key] = str(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    async def get_user_activity(
        db: AsyncSession,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        action_filter: Optional[AuditAction] = None,
        entity_type_filter: Optional[str] = None,
    ) -> list:
        """Get audit logs for a specific user."""
        query = select(AuditLog).where(AuditLog.user_id == user_id)
        
        if action_filter:
            query = query.where(AuditLog.action == action_filter)
        if entity_type_filter:
            query = query.where(AuditLog.entity_type == entity_type_filter)
        
        query = (
            query.order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_entity_history(
        db: AsyncSession,
        entity_type: str,
        entity_id: UUID,
        limit: int = 100,
    ) -> list:
        """Get complete audit history for a specific entity."""
        query = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        
        result = await db.execute(query)
        return result.scalars().all()


# Convenience functions for common audit patterns
async def log_create(
    db: AsyncSession,
    user: Optional[User],
    entity_type: str,
    entity_id: UUID,
    entity_name: Optional[str] = None,
    new_values: Optional[Dict] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Convenience function to log entity creation."""
    return await AuditService.log_action(
        db=db,
        user=user,
        action=AuditAction.CREATE,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        new_values=new_values,
        request=request,
        changes_summary=f"Created {entity_type}: {entity_name or entity_id}",
    )


async def log_update(
    db: AsyncSession,
    user: Optional[User],
    entity_type: str,
    entity_id: UUID,
    entity_name: Optional[str] = None,
    old_values: Optional[Dict] = None,
    new_values: Optional[Dict] = None,
    request: Optional[Request] = None,
    changes_summary: Optional[str] = None,
) -> AuditLog:
    """Convenience function to log entity update."""
    return await AuditService.log_action(
        db=db,
        user=user,
        action=AuditAction.UPDATE,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        old_values=old_values,
        new_values=new_values,
        request=request,
        changes_summary=changes_summary or f"Updated {entity_type}: {entity_name or entity_id}",
    )


async def log_delete(
    db: AsyncSession,
    user: Optional[User],
    entity_type: str,
    entity_id: UUID,
    entity_name: Optional[str] = None,
    old_values: Optional[Dict] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """Convenience function to log entity deletion."""
    return await AuditService.log_action(
        db=db,
        user=user,
        action=AuditAction.DELETE,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        old_values=old_values,
        request=request,
        changes_summary=f"Deleted {entity_type}: {entity_name or entity_id}",
    )
