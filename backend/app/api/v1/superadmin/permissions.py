"""
Super Admin Permissions Management API

Provides granular role-based access control (RBAC) management.
Only SUPER_ADMIN can access these endpoints.

Security:
- All endpoints protected by require_superadmin
- Audit logging for all permission changes
- Input validation and sanitization
- Rate limiting recommended at nginx level
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field, ConfigDict

from app.core.database import get_db
from app.core.rate_limiter import limiter
from app.core.security import require_superadmin
from app.models import User, RolePermission, UserRole
from app.services.audit_service import AuditService
from app.models.audit import AuditAction

router = APIRouter(prefix="/permissions", tags=["Super Admin - Permissions"])


# ============================================================================
# Schemas
# ============================================================================


class PermissionDefinition(BaseModel):
    """Individual permission definition."""

    model_config = ConfigDict(frozen=True)

    action: str = Field(
        ...,
        description="Action identifier (e.g., 'create', 'read', 'update', 'delete')",
    )
    description: str = Field(..., description="Human-readable description")
    scope: str = Field(
        default="own", description="Permission scope: 'own', 'team', 'all'"
    )
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")


class ModulePermissions(BaseModel):
    """Permissions for a specific module."""

    model_config = ConfigDict(frozen=True)

    module: str = Field(..., description="Module identifier")
    permissions: List[PermissionDefinition] = Field(default_factory=list)


class RolePermissionCreate(BaseModel):
    """Schema for creating/updating role permissions."""

    role: str = Field(..., min_length=1, max_length=50, description="Role identifier")
    module: str = Field(
        ..., min_length=1, max_length=50, description="Module identifier"
    )
    permissions: List[str] = Field(
        default_factory=list, description="List of allowed actions"
    )
    conditions: Optional[dict] = Field(
        default=None, description="Conditional permissions (JSON)"
    )
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: bool = Field(default=True)


class RolePermissionUpdate(BaseModel):
    """Schema for updating role permissions."""

    permissions: Optional[List[str]] = None
    conditions: Optional[dict] = None
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class RolePermissionResponse(BaseModel):
    """Response schema for role permissions."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    module: str
    permissions: List[str]
    conditions: Optional[dict]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoleSummary(BaseModel):
    """Summary of a role and its permissions."""

    role: str
    display_name: str
    user_count: int
    modules: List[str]
    is_system_role: bool


class PermissionCheckRequest(BaseModel):
    """Request to check if a user has a specific permission."""

    user_id: UUID
    module: str
    action: str
    resource_id: Optional[UUID] = None


class PermissionCheckResponse(BaseModel):
    """Response for permission check."""

    has_permission: bool
    reason: Optional[str] = None
    scope: Optional[str] = None  # 'own', 'team', 'all'


# ============================================================================
# System-defined permission matrix
# ============================================================================

SYSTEM_PERMISSIONS = {
    "users": [
        PermissionDefinition(
            action="create", description="Create new users", scope="all"
        ),
        PermissionDefinition(
            action="read", description="View user details", scope="all"
        ),
        PermissionDefinition(
            action="update", description="Update user information", scope="all"
        ),
        PermissionDefinition(action="delete", description="Delete users", scope="all"),
        PermissionDefinition(
            action="impersonate",
            description="Impersonate users",
            scope="all",
            requires_2fa=True,
        ),
        PermissionDefinition(
            action="block", description="Block/unblock users", scope="all"
        ),
        PermissionDefinition(
            action="export", description="Export user data", scope="all"
        ),
    ],
    "vendors": [
        PermissionDefinition(
            action="create", description="Create vendors", scope="all"
        ),
        PermissionDefinition(
            action="read", description="View vendor details", scope="all"
        ),
        PermissionDefinition(
            action="update", description="Update vendor information", scope="all"
        ),
        PermissionDefinition(
            action="delete", description="Delete vendors", scope="all"
        ),
        PermissionDefinition(
            action="approve", description="Approve pending vendors", scope="all"
        ),
        PermissionDefinition(
            action="suspend", description="Suspend vendors", scope="all"
        ),
        PermissionDefinition(
            action="export", description="Export vendor data", scope="all"
        ),
    ],
    "properties": [
        PermissionDefinition(
            action="create", description="Create properties", scope="all"
        ),
        PermissionDefinition(action="read", description="View properties", scope="all"),
        PermissionDefinition(
            action="update", description="Update properties", scope="all"
        ),
        PermissionDefinition(
            action="delete", description="Delete properties", scope="all"
        ),
        PermissionDefinition(
            action="feature", description="Feature/unfeature properties", scope="all"
        ),
        PermissionDefinition(
            action="moderate", description="Moderate property content", scope="all"
        ),
    ],
    "bookings": [
        PermissionDefinition(
            action="create", description="Create bookings", scope="all"
        ),
        PermissionDefinition(action="read", description="View bookings", scope="all"),
        PermissionDefinition(
            action="update", description="Update bookings", scope="all"
        ),
        PermissionDefinition(
            action="cancel", description="Cancel bookings", scope="all"
        ),
        PermissionDefinition(
            action="refund",
            description="Process refunds",
            scope="all",
            requires_2fa=True,
        ),
        PermissionDefinition(
            action="export", description="Export booking data", scope="all"
        ),
    ],
    "content": [
        PermissionDefinition(
            action="create", description="Create blog posts/pages", scope="all"
        ),
        PermissionDefinition(action="read", description="View content", scope="all"),
        PermissionDefinition(action="update", description="Edit content", scope="all"),
        PermissionDefinition(
            action="delete", description="Delete content", scope="all"
        ),
        PermissionDefinition(
            action="publish", description="Publish/unpublish content", scope="all"
        ),
        PermissionDefinition(
            action="seo", description="Manage SEO settings", scope="all"
        ),
    ],
    "tours": [
        PermissionDefinition(action="create", description="Create tours", scope="all"),
        PermissionDefinition(action="read", description="View tours", scope="all"),
        PermissionDefinition(action="update", description="Update tours", scope="all"),
        PermissionDefinition(action="delete", description="Delete tours", scope="all"),
    ],
    "chat": [
        PermissionDefinition(
            action="create", description="Start conversations", scope="all"
        ),
        PermissionDefinition(action="read", description="Read messages", scope="all"),
        PermissionDefinition(
            action="delete", description="Delete conversations", scope="all"
        ),
    ],
    "analytics": [
        PermissionDefinition(action="read", description="View analytics", scope="all"),
        PermissionDefinition(
            action="export", description="Export analytics data", scope="all"
        ),
        PermissionDefinition(
            action="reports", description="Generate reports", scope="all"
        ),
    ],
    "system": [
        PermissionDefinition(
            action="settings",
            description="Manage system settings",
            scope="all",
            requires_2fa=True,
        ),
        PermissionDefinition(
            action="maintenance",
            description="Enable/disable maintenance mode",
            scope="all",
            requires_2fa=True,
        ),
        PermissionDefinition(
            action="backup",
            description="Manage backups",
            scope="all",
            requires_2fa=True,
        ),
        PermissionDefinition(
            action="logs", description="View system logs", scope="all"
        ),
        PermissionDefinition(
            action="permissions",
            description="Manage permissions",
            scope="all",
            requires_2fa=True,
        ),
    ],
}


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/matrix", response_model=List[ModulePermissions])
async def get_permission_matrix(
    current_user: User = Depends(require_superadmin()),
) -> List[ModulePermissions]:
    """
    Get the complete permission matrix for all modules.

    Returns a structured list of all available permissions organized by module.
    This is used to build the permission configuration UI.
    """
    return [
        ModulePermissions(module=module, permissions=perms)
        for module, perms in SYSTEM_PERMISSIONS.items()
    ]


@router.get("/roles", response_model=List[RoleSummary])
async def get_all_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> List[RoleSummary]:
    """
    Get summary of all roles and their configured permissions.

    Includes user count per role and list of modules they have access to.
    """
    # Get all role permissions from database
    result = await db.execute(select(RolePermission).where(RolePermission.is_active))
    role_perms = result.scalars().all()

    # Group by role
    role_modules: dict = {}
    for rp in role_perms:
        if rp.role not in role_modules:
            role_modules[rp.role] = set()
        role_modules[rp.role].add(rp.module)

    # Get user counts per role
    role_counts = {}
    for role in UserRole:
        result = await db.execute(
            select(User).where(and_(User.role == role, User.is_active))
        )
        role_counts[role.value] = len(result.scalars().all())

    # Build response
    summaries = []
    system_roles = {
        "super_admin",
        "admin",
        "agent",
        "customer_service",
        "vendor",
        "client",
    }

    for role in UserRole:
        display_names = {
            "super_admin": "Super Administrator",
            "admin": "Administrator",
            "agent": "Sales Agent",
            "customer_service": "Customer Service",
            "vendor": "Vendor/Provider",
            "client": "Client/Customer",
        }

        summaries.append(
            RoleSummary(
                role=role.value,
                display_name=display_names.get(role.value, role.value),
                user_count=role_counts.get(role.value, 0),
                modules=sorted(list(role_modules.get(role.value, set()))),
                is_system_role=role.value in system_roles,
            )
        )

    return summaries


@router.get("/roles/{role}", response_model=List[RolePermissionResponse])
async def get_role_permissions(
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> List[RolePermissionResponse]:
    """
    Get all permissions configured for a specific role.
    """
    # Validate role exists
    try:
        UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {role}"
        )

    result = await db.execute(
        select(RolePermission)
        .where(RolePermission.role == role)
        .order_by(RolePermission.module)
    )
    permissions = result.scalars().all()

    return [RolePermissionResponse.model_validate(p) for p in permissions]


@router.post("/roles/{role}/modules/{module}", response_model=RolePermissionResponse)
@limiter.limit("10/minute")
async def set_role_permissions(
    request: Request,
    role: str,
    module: str,
    data: RolePermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> RolePermissionResponse:
    """
    Set permissions for a role on a specific module.

    Creates new or updates existing permission configuration.
    Audits the change for security tracking.
    """
    # Validate role
    try:
        UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {role}"
        )

    # Validate module exists in system
    if module not in SYSTEM_PERMISSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid module: {module}"
        )

    # Validate permissions are valid for this module
    valid_actions = {p.action for p in SYSTEM_PERMISSIONS[module]}
    invalid_perms = set(data.permissions) - valid_actions
    if invalid_perms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permissions for module {module}: {invalid_perms}",
        )

    # Check for existing permission record
    result = await db.execute(
        select(RolePermission).where(
            and_(RolePermission.role == role, RolePermission.module == module)
        )
    )
    existing = result.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if existing:
        # Update existing
        old_perms = existing.permissions.copy()

        existing.permissions = data.permissions
        existing.conditions = data.conditions
        existing.description = data.description
        existing.is_active = data.is_active
        existing.updated_at = now

        # Audit log
        await AuditService.log_audit_action(
            db=db,
            user=current_user,
            action=AuditAction.UPDATE,
            entity_type="role_permission",
            entity_id=existing.id,
            entity_name=f"{role}.{module}",
            old_values={"permissions": old_perms},
            new_values={"permissions": data.permissions},
            changes_summary=f"Updated permissions for {role} on {module}",
        )

        await db.commit()
        return RolePermissionResponse.model_validate(existing)

    else:
        # Create new
        new_perm = RolePermission(
            role=role,
            module=module,
            permissions=data.permissions,
            conditions=data.conditions,
            description=data.description,
            is_active=data.is_active,
            created_at=now,
            updated_at=now,
        )

        db.add(new_perm)
        await db.flush()

        # Audit log
        await AuditService.log_audit_action(
            db=db,
            user=current_user,
            action=AuditAction.CREATE,
            entity_type="role_permission",
            entity_id=new_perm.id,
            entity_name=f"{role}.{module}",
            new_values={"permissions": data.permissions},
            changes_summary=f"Created permissions for {role} on {module}",
        )

        await db.commit()
        return RolePermissionResponse.model_validate(new_perm)


@router.put("/roles/{role}/modules/{module}", response_model=RolePermissionResponse)
@limiter.limit("10/minute")
async def update_role_permissions(
    request: Request,
    role: str,
    module: str,
    data: RolePermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> RolePermissionResponse:
    """
    Partially update permissions for a role on a specific module.
    """
    result = await db.execute(
        select(RolePermission).where(
            and_(RolePermission.role == role, RolePermission.module == module)
        )
    )
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission configuration not found for {role}.{module}",
        )

    old_values = {}
    new_values = {}

    if data.permissions is not None:
        # Validate
        valid_actions = {p.action for p in SYSTEM_PERMISSIONS.get(module, [])}
        invalid_perms = set(data.permissions) - valid_actions
        if invalid_perms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid permissions: {invalid_perms}",
            )
        old_values["permissions"] = existing.permissions.copy()
        new_values["permissions"] = data.permissions
        existing.permissions = data.permissions

    if data.conditions is not None:
        old_values["conditions"] = existing.conditions
        new_values["conditions"] = data.conditions
        existing.conditions = data.conditions

    if data.description is not None:
        old_values["description"] = existing.description
        new_values["description"] = data.description
        existing.description = data.description

    if data.is_active is not None:
        old_values["is_active"] = existing.is_active
        new_values["is_active"] = data.is_active
        existing.is_active = data.is_active

    existing.updated_at = datetime.now(timezone.utc)

    # Audit log
    await AuditService.log_audit_action(
        db=db,
        user=current_user,
        action=AuditAction.UPDATE,
        entity_type="role_permission",
        entity_id=existing.id,
        entity_name=f"{role}.{module}",
        old_values=old_values if old_values else None,
        new_values=new_values if new_values else None,
        changes_summary=f"Updated {role}.{module} configuration",
    )

    await db.commit()
    return RolePermissionResponse.model_validate(existing)


@router.delete("/roles/{role}/modules/{module}", response_model=dict)
async def delete_role_permissions(
    role: str,
    module: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> dict:
    """
    Delete permission configuration for a role on a module.

    This removes all custom permissions - the role will have no access
    to this module unless system defaults apply.
    """
    result = await db.execute(
        select(RolePermission).where(
            and_(RolePermission.role == role, RolePermission.module == module)
        )
    )
    existing = result.scalar_one_or_none()

    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission configuration not found",
        )

    perm_id = existing.id
    perm_data = {
        "role": existing.role,
        "module": existing.module,
        "permissions": existing.permissions.copy(),
    }

    await db.delete(existing)

    # Audit log
    await AuditService.log_audit_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="role_permission",
        entity_id=perm_id,
        entity_name=f"{role}.{module}",
        old_values=perm_data,
        changes_summary=f"Deleted permission configuration for {role}.{module}",
    )

    await db.commit()

    return {"message": f"Permission configuration for {role}.{module} deleted"}


@router.post("/check", response_model=PermissionCheckResponse)
@limiter.limit("30/minute")
async def check_permission(
    request: Request,
    data: PermissionCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> PermissionCheckResponse:
    """
    Check if a specific user has a permission.

    Used for testing and debugging permission configurations.
    """
    # Get target user
    result = await db.execute(select(User).where(User.id == data.user_id))
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get role permissions
    result = await db.execute(
        select(RolePermission).where(
            and_(
                RolePermission.role == target_user.role,
                RolePermission.module == data.module,
                RolePermission.is_active,
            )
        )
    )
    role_perm = result.scalar_one_or_none()

    if not role_perm:
        return PermissionCheckResponse(
            has_permission=False,
            reason=f"No permissions configured for {target_user.role} on {data.module}",
        )

    has_perm = data.action in role_perm.permissions

    # Determine scope from permission definition
    scope = None
    if has_perm and data.module in SYSTEM_PERMISSIONS:
        for perm in SYSTEM_PERMISSIONS[data.module]:
            if perm.action == data.action:
                scope = perm.scope
                break

    return PermissionCheckResponse(
        has_permission=has_perm,
        reason=None if has_perm else f"Action '{data.action}' not in role permissions",
        scope=scope,
    )


@router.post("/roles/{role}/reset", response_model=dict)
@limiter.limit("5/minute")
async def reset_role_to_defaults(
    request: Request,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin()),
) -> dict:
    """
    Reset a role's permissions to system defaults.

    WARNING: This will delete all custom permission configurations for this role.
    """
    # Validate role
    try:
        UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid role: {role}"
        )

    # Delete all existing permissions for this role
    result = await db.execute(select(RolePermission).where(RolePermission.role == role))
    existing_perms = result.scalars().all()

    deleted_count = len(existing_perms)

    for perm in existing_perms:
        await db.delete(perm)

    # Audit log
    await AuditService.log_audit_action(
        db=db,
        user=current_user,
        action=AuditAction.DELETE,
        entity_type="role_permission",
        entity_id=None,
        entity_name=f"{role}.*",
        changes_summary=f"Reset all permissions for role {role} to defaults ({deleted_count} configurations deleted)",
    )

    await db.commit()

    return {
        "message": f"Role {role} permissions reset to defaults",
        "deleted_configurations": deleted_count,
    }
