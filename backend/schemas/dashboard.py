from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class PaginationParams(BaseModel):
    """Parameters for pagination in dashboard lists."""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")

class DashboardFilters(BaseModel):
    """Filter parameters for fetching leads."""
    search_query: Optional[str] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    priority: Optional[str] = None
    is_qualified: Optional[bool] = None
    industry: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class LeadSummaryDTO(BaseModel):
    """A lightweight summary of a lead for list views."""
    lead_id: uuid.UUID
    email: str
    company_domain: str
    status: Optional[str]
    score: Optional[int]
    confidence: Optional[float]
    qualified: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    """Response model for a paginated list of leads."""
    total_count: int
    page: int
    size: int
    items: List[LeadSummaryDTO]

class LeadDetailsResponse(BaseModel):
    """Comprehensive details for a single lead."""
    lead_id: uuid.UUID
    email: str
    company_domain: str
    status: Optional[str]
    created_at: datetime
    
    # Nested aggregated data
    score: Optional[int] = None
    confidence: Optional[float] = None
    qualification_status: Optional[bool] = None
    qualification_reason: Optional[str] = None
    
    # We leave these as generic dicts because they map to complex JSONB structures
    company_profile: Optional[Dict[str, Any]] = None
    industry_classification: Optional[Dict[str, Any]] = None
    recommendation: Optional[Dict[str, Any]] = None
    company_research: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    """Aggregated statistics for the dashboard overview."""
    total_leads: int
    qualified_leads: int
    unqualified_leads: int
    high_score_leads: int
    average_score: float
    leads_by_status: Dict[str, int]
    
class AnalyticsResponse(BaseModel):
    """Deeper analytical insights."""
    top_industries: Dict[str, int]
    score_distribution: Dict[str, int]
    
class OverviewResponse(BaseModel):
    """A high-level dashboard overview combining stats and recent activity."""
    statistics: StatisticsResponse
    recent_leads: List[LeadSummaryDTO]
