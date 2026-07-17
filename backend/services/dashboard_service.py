"""
backend.services.dashboard_service

Implements the DashboardService, providing complex read-only queries and aggregations
for the dashboard APIs. Uses SQLAlchemy directly to avoid modifying existing repositories.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_

from backend.models.raw_lead import RawLead
from backend.models.lead_score import LeadScore
from backend.models.lead_qualification import LeadQualification
from backend.schemas.dashboard import (
    PaginationParams,
    DashboardFilters,
    LeadSummaryDTO,
    LeadListResponse,
    LeadDetailsResponse,
    StatisticsResponse,
    OverviewResponse,
    AnalyticsResponse
)

logger = logging.getLogger(__name__)

class DashboardService:
    """
    Read-only service for dashboard queries. 
    Strictly queries existing models without mutating data.
    """
    
    def get_dashboard_overview(self, db: Session) -> OverviewResponse:
        """Returns the high-level dashboard overview."""
        stats = self.get_statistics(db)
        recent = self.get_recent_leads(db, limit=5)
        return OverviewResponse(statistics=stats, recent_leads=recent)

    def get_statistics(self, db: Session) -> StatisticsResponse:
        """Computes system-wide lead statistics."""
        total = db.query(RawLead).count()
        
        # Qualified
        qualified = db.query(LeadQualification).filter(LeadQualification.qualified == True).count()
        unqualified = db.query(LeadQualification).filter(LeadQualification.qualified == False).count()
        
        # High score
        high_score = db.query(LeadScore).filter(LeadScore.score >= 80).count()
        
        # Avg score
        avg = db.query(func.avg(LeadScore.score)).scalar()
        avg_score = float(avg) if avg else 0.0
        
        # Group by status
        status_counts = db.query(RawLead.status, func.count(RawLead.lead_id)).group_by(RawLead.status).all()
        leads_by_status = {status or "unknown": count for status, count in status_counts}
        
        return StatisticsResponse(
            total_leads=total,
            qualified_leads=qualified,
            unqualified_leads=unqualified,
            high_score_leads=high_score,
            average_score=round(avg_score, 2),
            leads_by_status=leads_by_status
        )

    def get_recent_leads(self, db: Session, limit: int = 5) -> List[LeadSummaryDTO]:
        """Fetches the most recently added leads."""
        query = db.query(RawLead)\
            .options(joinedload(RawLead.lead_score), joinedload(RawLead.lead_qualification))\
            .order_by(desc(RawLead.created_at))\
            .limit(limit)
            
        leads = query.all()
        return [self._map_to_summary(lead) for lead in leads]

    def search_leads(self, db: Session, filters: DashboardFilters, pagination: PaginationParams) -> LeadListResponse:
        """Searches and filters leads with pagination."""
        query = db.query(RawLead)\
            .options(joinedload(RawLead.lead_score), joinedload(RawLead.lead_qualification))
            
        # Apply filters
        if filters.search_query:
            search = f"%{filters.search_query}%"
            query = query.filter(or_(
                RawLead.email.ilike(search),
                RawLead.company_domain.ilike(search)
            ))
            
        if filters.min_score is not None or filters.max_score is not None:
            query = query.join(LeadScore)
            if filters.min_score is not None:
                query = query.filter(LeadScore.score >= filters.min_score)
            if filters.max_score is not None:
                query = query.filter(LeadScore.score <= filters.max_score)
                
        if filters.is_qualified is not None:
            # Need outerjoin or join depending on if we strictly want records with qualification models
            query = query.join(LeadQualification).filter(LeadQualification.qualified == filters.is_qualified)
            
        # Sort and Pagination
        query = query.order_by(desc(RawLead.created_at))
        
        total_count = query.count()
        offset = (pagination.page - 1) * pagination.size
        leads = query.offset(offset).limit(pagination.size).all()
        
        items = [self._map_to_summary(lead) for lead in leads]
        
        return LeadListResponse(
            total_count=total_count,
            page=pagination.page,
            size=pagination.size,
            items=items
        )

    def get_lead_details(self, db: Session, lead_id: uuid.UUID) -> Optional[LeadDetailsResponse]:
        """Fetches comprehensive details for a single lead without N+1."""
        lead = db.query(RawLead)\
            .options(
                joinedload(RawLead.lead_score),
                joinedload(RawLead.lead_qualification),
                joinedload(RawLead.company_profile),
                joinedload(RawLead.industry_classification),
                joinedload(RawLead.recommendation)
            )\
            .filter(RawLead.lead_id == lead_id).first()
            
        if not lead:
            return None
            
        return LeadDetailsResponse(
            lead_id=lead.lead_id,
            email=lead.email,
            company_domain=lead.company_domain,
            status=lead.status,
            created_at=lead.created_at,
            score=lead.lead_score.score if lead.lead_score else None,
            confidence=float(lead.lead_score.confidence) if lead.lead_score and lead.lead_score.confidence else None,
            qualification_status=lead.lead_qualification.qualified if lead.lead_qualification else None,
            qualification_reason=lead.lead_qualification.reason if lead.lead_qualification else None,
            # We map JSONB fields natively
            company_profile=lead.company_profile.profile_data if lead.company_profile else None,
            industry_classification=lead.industry_classification.classification_data if lead.industry_classification else None,
            recommendation=lead.recommendation.recommendation_data if lead.recommendation else None
        )

    def get_analytics(self, db: Session) -> AnalyticsResponse:
        """Returns deeper aggregated insights."""
        # Note: True industry analytics requires querying the JSONB, which varies by dialect.
        # Returning stubbed dictionary structures here to maintain DB-agnostic behavior 
        # unless JSONB querying is explicitly modeled.
        
        # Example for score distribution via bucket grouping logic
        scores = db.query(LeadScore.score).all()
        distribution = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        
        for (s,) in scores:
            if s is None: continue
            if s <= 20: distribution["0-20"] += 1
            elif s <= 40: distribution["21-40"] += 1
            elif s <= 60: distribution["41-60"] += 1
            elif s <= 80: distribution["61-80"] += 1
            else: distribution["81-100"] += 1
            
        return AnalyticsResponse(
            top_industries={"Technology": 10, "Finance": 5, "Healthcare": 3}, # Stubbed
            score_distribution=distribution
        )

    def _map_to_summary(self, lead: RawLead) -> LeadSummaryDTO:
        """Helper to map SQLAlchemy model to DTO."""
        score = lead.lead_score.score if lead.lead_score else None
        conf = float(lead.lead_score.confidence) if lead.lead_score and lead.lead_score.confidence else None
        qual = lead.lead_qualification.qualified if lead.lead_qualification else None
        
        return LeadSummaryDTO(
            lead_id=lead.lead_id,
            email=lead.email,
            company_domain=lead.company_domain,
            status=lead.status,
            score=score,
            confidence=conf,
            qualified=qual,
            created_at=lead.created_at
        )

dashboard_service = DashboardService()
