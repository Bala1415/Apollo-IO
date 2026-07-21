from fastapi import APIRouter
from backend.api.health import router as health_router
from backend.api.lead_routes import router as lead_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(lead_router, prefix="/leads", tags=["leads"])
