import uuid
import time
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from backend.config import get_settings

logger = logging.getLogger("apollo.api.middleware")

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique correlation ID into every request for tracing.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs structured information about incoming HTTP requests.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        logger.info(f"[{correlation_id}] Request Started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                f"[{correlation_id}] Request Completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Duration: {process_time:.3f}s"
            )
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{correlation_id}] Request Failed: {request.method} {request.url.path} "
                f"- Error: {str(e)} - Duration: {process_time:.3f}s"
            )
            raise

def register_middleware(app: FastAPI) -> None:
    """Registers all application middleware."""
    settings = get_settings()
    
    # Custom Middlewares (Registered in reverse order of execution)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    
    # Standard Starlette Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.security.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID", "X-Process-Time"]
    )
    
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"] # In production, restrict this based on settings
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    logger.info("Registered infrastructure middleware.")
