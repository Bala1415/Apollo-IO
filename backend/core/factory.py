import logging
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.core.lifespan import lifespan
from backend.core.middleware import CorrelationIdMiddleware, RequestLoggingMiddleware
from backend.core.metrics import PrometheusMiddleware, metrics_endpoint
from backend.core.middleware import register_middleware
from backend.core.exceptions import register_exception_handlers
from backend.core.health import run_comprehensive_health_check

logger = logging.getLogger("apollo.api.factory")

def create_app() -> FastAPI:
    """
    Application Factory for Apollo-IO FastAPI backend.
    Assembles configuration, middleware, exception handlers, and the lifespan manager.
    """
    settings = get_settings()
    
    # 1. Initialize Application Metadata
    app = FastAPI(
        title=settings.app.name,
        description="Apollo-IO AI-powered Lead Intelligence Platform API",
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        contact={
            "name": "Apollo-IO Architecture Team",
        }
    )

    # 2. Register Global Exception Handlers
    register_exception_handlers(app)

    # 3. Add Custom Middlewares (Executed bottom-up, so top is outermost)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(PrometheusMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    register_middleware(app)

    # 4. Router Registration Framework
    from backend.api.routes import api_router
    # 5. Include API Routers
    app.include_router(api_router)
    
    # 6. Include System Endpoints (Metrics)
    app.add_route("/metrics", metrics_endpoint, methods=["GET"])
    
    # Register bare health routes at root (optional but common practice for probes)
    from backend.api.health import router as root_health_router
    app.include_router(root_health_router)
    
    logger.info("Application Factory successfully constructed the FastAPI instance.")
    return app
