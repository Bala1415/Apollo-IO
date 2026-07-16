import uuid
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .raw_lead import RawLead


class CompanyProfile(Base, TimestampMixin):
    __tablename__ = "company_profile"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("raw_leads.lead_id", ondelete="CASCADE"), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    company_size: Mapped[Optional[str]] = mapped_column(String)
    tech_stack: Mapped[Optional[list[Any]]] = mapped_column(JSONB)
    locations: Mapped[Optional[list[Any]]] = mapped_column(JSONB)

    lead: Mapped["RawLead"] = relationship("RawLead", back_populates="company_profile")
