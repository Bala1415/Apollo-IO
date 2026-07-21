from fastapi import APIRouter

from backend.api.health import router as health_router
from backend.api.lead_routes import router as lead_router
from backend.api.company_routes import router as company_router
from backend.api.report_routes import router as report_router
from backend.api.notification_routes import router as notification_router
from backend.api.auth_routes import router as auth_router
from backend.api.dashboard_routes import router as dashboard_router
from backend.api.extension_routes import router as extension_router

# Master Router Prefix
api_router = APIRouter(prefix="/api/v1")

# Include infrastructure and operational routes (Health does not get /api/v1 typically, but we can register it here or on app)
# Wait, standard health is usually at root. We'll register health on the master router anyway.
api_router.include_router(health_router)

# Include Authentication
api_router.include_router(auth_router)

# Include business domain routes
api_router.include_router(lead_router)
api_router.include_router(company_router)
api_router.include_router(report_router)
api_router.include_router(notification_router)
api_router.include_router(dashboard_router)
api_router.include_router(extension_router)
