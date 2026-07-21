import uuid
from typing import Optional, Any, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.types import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .raw_lead import RawLead


class CompanyResearch(Base, TimestampMixin):
    __tablename__ = "company_research"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("raw_leads.lead_id", ondelete="CASCADE"), nullable=False, unique=True)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    products: Mapped[Optional[list[Any]]] = mapped_column(JSON)
    services: Mapped[Optional[list[Any]]] = mapped_column(JSON)
    employees: Mapped[Optional[int]] = mapped_column(Integer)
    funding: Mapped[Optional[str]] = mapped_column(String)
    news: Mapped[Optional[list[Any]]] = mapped_column(JSON)

    lead: Mapped["RawLead"] = relationship("RawLead", back_populates="company_research")
