from typing import Annotated
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models import User, UserRole
from app.schemas import PaginationParams

SessionDep = Annotated[AsyncSession, Depends(get_db)]

CurrentUserDep = Annotated[User, Depends(get_current_user)]

PaginationDep = Annotated[PaginationParams, Query()]

VendorDep = Annotated[User, Depends(require_role(UserRole.VENDOR))]
AdminDep = Annotated[User, Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))]
SuperAdminDep = Annotated[User, Depends(require_role(UserRole.SUPER_ADMIN))]
