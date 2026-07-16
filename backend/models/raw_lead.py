import uuid
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .company_research import CompanyResearch
    from .company_profile import CompanyProfile
    from .industry_classification import IndustryClassification
    from .lead_qualification import LeadQualification
    from .lead_score import LeadScore
    from .recommendation import Recommendation


class RawLead(Base, TimestampMixin):
    __tablename__ = "raw_leads"

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company_domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    browser_history: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    interest_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[Optional[str]] = mapped_column(String, default="new")

    # Relationships
    company_research: Mapped[Optional["CompanyResearch"]] = relationship("CompanyResearch", back_populates="lead", cascade="all, delete-orphan", uselist=False)
    company_profile: Mapped[Optional["CompanyProfile"]] = relationship("CompanyProfile", back_populates="lead", cascade="all, delete-orphan", uselist=False)
    industry_classification: Mapped[Optional["IndustryClassification"]] = relationship("IndustryClassification", back_populates="lead", cascade="all, delete-orphan", uselist=False)
    lead_qualification: Mapped[Optional["LeadQualification"]] = relationship("LeadQualification", back_populates="lead", cascade="all, delete-orphan", uselist=False)
    lead_score: Mapped[Optional["LeadScore"]] = relationship("LeadScore", back_populates="lead", cascade="all, delete-orphan", uselist=False)
    recommendation: Mapped[Optional["Recommendation"]] = relationship("Recommendation", back_populates="lead", cascade="all, delete-orphan", uselist=False)
