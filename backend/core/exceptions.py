import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.exceptions import ApolloBaseException, ValidationError

logger = logging.getLogger("apollo.api.exceptions")

def _create_error_response(status_code: int, error_code: str, message: str, details: list = None) -> JSONResponse:
    """Standardized JSON structure for all API errors."""
    content = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    if details:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content)

async def apollo_base_exception_handler(request: Request, exc: ApolloBaseException) -> JSONResponse:
    """Handles domain-specific exceptions."""
    logger.warning(f"Domain Exception: {str(exc)}", exc_info=exc)
    
    if isinstance(exc, ValidationError):
        return _create_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=str(exc)
        )
        
    return _create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="BAD_REQUEST",
        message=str(exc)
    )

async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles FastAPI Pydantic validation errors."""
    logger.warning(f"Request Validation Error on {request.url.path}: {exc.errors()}")
    details = [
        {"loc": ".".join(map(str, err.get("loc", []))), "msg": err.get("msg"), "type": err.get("type")}
        for err in exc.errors()
    ]
    return _create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_code="UNPROCESSABLE_ENTITY",
        message="Request payload validation failed.",
        details=details
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handles explicit HTTP exceptions raised within routes."""
    logger.warning(f"HTTP Exception {exc.status_code}: {exc.detail}")
    return _create_error_response(
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        message=str(exc.detail)
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled server errors."""
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=exc)
    return _create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred."
    )

def register_exception_handlers(app: FastAPI) -> None:
    """Registers all custom exception handlers to the FastAPI application."""
    app.add_exception_handler(ApolloBaseException, apollo_base_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    logger.info("Registered global exception handlers.")
