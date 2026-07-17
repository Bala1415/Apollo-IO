from fastapi import APIRouter, Response, status
from backend.core.health import run_comprehensive_health_check
from backend.schemas.response import StandardResponse, success_response, error_response

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=StandardResponse[dict])
async def health_check(response: Response):
    """Deep health check verifying all dependencies (Database, Providers)."""
    health_data = run_comprehensive_health_check()
    if health_data["status"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return error_response(
            message="Service Degraded", 
            metadata={"checks": health_data["checks"]}
        )
    return success_response(data=health_data, message="System Healthy")

@router.get("/ready", response_model=StandardResponse[str])
async def readiness_probe():
    """Readiness probe for Kubernetes or Load Balancers."""
    return success_response(data="Ready to accept traffic")

@router.get("/live", response_model=StandardResponse[str])
async def liveness_probe():
    """Liveness probe for Kubernetes or Load Balancers."""
    return success_response(data="Alive")
