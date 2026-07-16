import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .raw_lead import RawLead


class LeadQualification(Base, TimestampMixin):
    __tablename__ = "lead_qualification"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("raw_leads.lead_id", ondelete="CASCADE"), nullable=False, unique=True)
    qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    reason: Mapped[Optional[str]] = mapped_column(Text)

    lead: Mapped["RawLead"] = relationship("RawLead", back_populates="lead_qualification")
