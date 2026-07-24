from fastapi import APIRouter
from backend.api.health import router as health_router
from backend.api.lead_routes import router as lead_router
from backend.api.extension_routes import router as extension_router
from backend.api.company_routes import router as company_router
from backend.api.dashboard_routes import router as dashboard_router
from backend.api.notification_routes import router as notification_router
from backend.api.report_routes import router as report_router
from backend.api.auth_routes import router as auth_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(lead_router, prefix="/leads", tags=["leads"])
router.include_router(extension_router, tags=["extension"])
router.include_router(company_router, tags=["companies"])
router.include_router(dashboard_router, tags=["dashboard"])
router.include_router(notification_router, tags=["notifications"])
router.include_router(report_router, tags=["reports"])
router.include_router(auth_router, tags=["auth"])
