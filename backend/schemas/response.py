from typing import Generic, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    """Standardized API response envelope."""
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="Human-readable message about the result")
    data: Optional[T] = Field(None, description="The primary payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Pagination or additional metadata")
    trace_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Response timestamp in ISO 8601 format"
    )

def success_response(
    data: Any = None, 
    message: str = "Success", 
    metadata: Optional[Dict[str, Any]] = None, 
    trace_id: Optional[str] = None
) -> StandardResponse:
    """Helper to create a standard success response."""
    return StandardResponse(
        success=True,
        message=message,
        data=data,
        metadata=metadata or {},
        trace_id=trace_id
    )

def error_response(
    message: str, 
    trace_id: Optional[str] = None, 
    metadata: Optional[Dict[str, Any]] = None
) -> StandardResponse:
    """Helper to create a standard error response."""
    return StandardResponse(
        success=False,
        message=message,
        data=None,
        metadata=metadata or {},
        trace_id=trace_id
    )
