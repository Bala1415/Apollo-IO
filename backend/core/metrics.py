import time
import logging
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger("apollo.core.metrics")

# --- Prometheus Metrics Definitions ---
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration",
    ["method", "endpoint"]
)

BACKGROUND_JOBS_TOTAL = Counter(
    "background_jobs_executed_total",
    "Total Background Jobs Executed",
    ["task_name", "status"]
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to intercept HTTP requests and record Prometheus metrics.
    Tracks request count, duration, and response status codes.
    """
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        method = request.method
        # We use the URL path. In a real system, you'd want to map to route templates to prevent cardinality explosion (e.g., /leads/{id} instead of /leads/12345).
        # For simplicity in this demo, we'll just track the raw path.
        path = request.url.path
        
        # Exclude metrics endpoint itself to prevent noise
        if path == "/metrics":
            return await call_next(request)

        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # If an unhandled exception bubbles up, it's a 500
            status_code = 500
            HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code=str(status_code)).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(time.time() - start_time)
            raise e
            
        process_time = time.time() - start_time
        
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code=str(status_code)).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(process_time)
        
        # Add a custom header for execution timing
        response.headers["X-Process-Time"] = str(process_time)
        return response

def metrics_endpoint() -> Response:
    """
    FastAPI endpoint handler to expose Prometheus metrics.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
