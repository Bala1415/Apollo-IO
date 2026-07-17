"""
backend.api.dashboard_routes

Exposes the REST API endpoints for the dashboard layer.
Strictly read-only routes, integrating with the DashboardService.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.User import User
from backend.security.dependencies import require_permissions
from backend.services.dashboard_service import dashboard_service
from backend.schemas.dashboard import (
    OverviewResponse,
    StatisticsResponse,
    LeadListResponse,
    LeadDetailsResponse,
    AnalyticsResponse,
    PaginationParams,
    DashboardFilters
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
logger = logging.getLogger(__name__)

@router.get("/overview", response_model=OverviewResponse)
def get_overview(
    current_user: User = Security(require_permissions(["dashboard:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves the high-level dashboard overview, including statistics 
    and recently processed leads.
    """
    try:
        return dashboard_service.get_dashboard_overview(db)
    except Exception as e:
        logger.error(f"Failed to fetch overview: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics(
    current_user: User = Security(require_permissions(["dashboard:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves aggregated platform statistics.
    """
    try:
        return dashboard_service.get_statistics(db)
    except Exception as e:
        logger.error(f"Failed to fetch statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Security(require_permissions(["dashboard:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves deep analytical insights (e.g. score distribution).
    """
    try:
        return dashboard_service.get_analytics(db)
    except Exception as e:
        logger.error(f"Failed to fetch analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leads", response_model=LeadListResponse)
def get_leads(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search_query: str = Query(None),
    min_score: int = Query(None),
    max_score: int = Query(None),
    is_qualified: bool = Query(None),
    current_user: User = Security(require_permissions(["dashboard:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves a paginated list of leads with optional filtering.
    """
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = DashboardFilters(
            search_query=search_query,
            min_score=min_score,
            max_score=max_score,
            is_qualified=is_qualified
        )
        return dashboard_service.search_leads(db, filters, pagination)
    except Exception as e:
        logger.error(f"Failed to search leads: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/leads/{lead_id}", response_model=LeadDetailsResponse)
def get_lead_details(
    lead_id: uuid.UUID, 
    current_user: User = Security(require_permissions(["dashboard:read"])),
    db: Session = Depends(get_db)
):
    """
    Retrieves the comprehensive intelligence dossier for a single lead.
    """
    try:
        details = dashboard_service.get_lead_details(db, lead_id)
        if not details:
            raise HTTPException(status_code=404, detail="Lead not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=LeadListResponse)
def search_leads_endpoint(
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Security(require_permissions(["dashboard:read"])),
    db: Session = Depends(get_db)
):
    """
    Alias for /leads with mandatory search query.
    """
    try:
        pagination = PaginationParams(page=page, size=size)
        filters = DashboardFilters(search_query=q)
        return dashboard_service.search_leads(db, filters, pagination)
    except Exception as e:
        logger.error(f"Search failed for '{q}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
