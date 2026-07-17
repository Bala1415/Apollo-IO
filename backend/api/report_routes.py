import uuid
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Request, Security
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.User import User
from backend.security.dependencies import require_permissions
from backend.schemas.response import StandardResponse, success_response
from backend.schemas.report import ReportResponse, ReportListResponse

router = APIRouter(prefix="/reports", tags=["Reports"])
logger = logging.getLogger(__name__)

@router.get("", response_model=StandardResponse[ReportListResponse])
async def list_reports(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Security(require_permissions(["report:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves a paginated list of generated AI dossiers.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    
    # Stub for fetching reports
    reports = [
        ReportResponse(
            id=uuid.uuid4(),
            lead_id=uuid.uuid4(),
            content="# AI Dossier\n\nGenerated content...",
            generated_at=datetime.now(timezone.utc),
            status="COMPLETED"
        )
    ]
    
    result = ReportListResponse(
        reports=reports,
        total_count=1,
        page=page,
        size=size
    )
    
    return success_response(data=result, trace_id=correlation_id)

@router.get("/{report_id}", response_model=StandardResponse[ReportResponse])
async def get_report(
    report_id: uuid.UUID,
    request: Request,
    current_user: User = Security(require_permissions(["report:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific report by ID.
    """
    correlation_id = getattr(request.state, "correlation_id", None)
    
    report = ReportResponse(
        id=report_id,
        lead_id=uuid.uuid4(),
        content="# AI Dossier\n\nThis is a highly detailed report.",
        generated_at=datetime.now(timezone.utc),
        status="COMPLETED"
    )
    
    return success_response(data=report, trace_id=correlation_id)

@router.get("/{report_id}/download", response_class=PlainTextResponse)
async def download_report(
    report_id: uuid.UUID,
    current_user: User = Security(require_permissions(["report:export"])),
    db: Session = Depends(get_db)
):
    """
    Downloads the report as a raw markdown file.
    """
    # Stub for generating download content
    content = f"# AI Dossier {report_id}\n\nDownloaded raw markdown content."
    return PlainTextResponse(
        content=content, 
        headers={"Content-Disposition": f"attachment; filename=dossier_{report_id}.md"}
    )
