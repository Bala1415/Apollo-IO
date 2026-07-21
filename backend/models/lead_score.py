import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .raw_lead import RawLead


class LeadScore(Base, TimestampMixin):
    __tablename__ = "lead_scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("raw_leads.lead_id", ondelete="CASCADE"), nullable=False, unique=True)
    score: Mapped[Optional[int]] = mapped_column(Integer)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))

    lead: Mapped["RawLead"] = relationship("RawLead", back_populates="lead_score")
