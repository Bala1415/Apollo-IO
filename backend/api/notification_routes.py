import uuid
import logging
from typing import List, Any
from fastapi import APIRouter, Depends, Query, Request, Security
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.User import User
from backend.security.dependencies import require_permissions
from backend.schemas.response import StandardResponse, success_response

router = APIRouter(prefix="/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)

@router.get("", response_model=StandardResponse[List[Any]])
async def list_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Security(require_permissions(["notification:send"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves a paginated list of sent notifications.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    
    # Stub for fetching notifications
    notifications = []
    
    return success_response(
        data=notifications, 
        trace_id=correlation_id,
        metadata={"total_count": 0, "page": page, "size": size}
    )

@router.get("/{notification_id}", response_model=StandardResponse[Any])
async def get_notification(
    notification_id: uuid.UUID,
    request: Request,
    current_user: User = Security(require_permissions(["notification:send"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific notification by ID.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    return success_response(data={"id": notification_id, "status": "DELIVERED"}, trace_id=correlation_id)

@router.post("/{notification_id}/resend", response_model=StandardResponse[bool])
async def resend_notification(
    notification_id: uuid.UUID,
    request: Request,
    current_user: User = Security(require_permissions(["notification:send"])),
    db: Session = Depends(get_db)
):
    """
    Attempts to resend a failed notification.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    return success_response(data=True, message="Notification resend queued", trace_id=correlation_id)
