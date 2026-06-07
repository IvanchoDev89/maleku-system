from fastapi import APIRouter

from .audit import router as audit_router
from .content import router as content_router
from .dashboard import router as dashboard_router
from .permissions import router as permissions_router
from .settings import router as settings_router
from .system import router as system_router
from .users import router as users_router
from .vendors import router as vendors_router

router = APIRouter()
router.include_router(audit_router, prefix="/audit")
router.include_router(content_router)
router.include_router(dashboard_router, prefix="/dashboard")
router.include_router(permissions_router)
router.include_router(settings_router)
router.include_router(system_router, prefix="/system")
router.include_router(users_router, prefix="/users")
router.include_router(vendors_router)
