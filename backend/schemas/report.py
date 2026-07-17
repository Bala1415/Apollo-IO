from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import uuid
from datetime import datetime

class ReportResponse(BaseModel):
    """Schema representing an AI-generated dossier report."""
    id: uuid.UUID
    lead_id: uuid.UUID
    content: str
    format: str = "markdown"
    generated_at: datetime
    status: str

class ReportListResponse(BaseModel):
    """Schema for a paginated list of reports."""
    reports: List[ReportResponse]
    total_count: int
    page: int
    size: int
