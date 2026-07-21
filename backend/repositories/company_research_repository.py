from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.models.company_research import CompanyResearch
from backend.repositories.base_repository import BaseRepository

class CompanyResearchRepository(BaseRepository[CompanyResearch]):
    def __init__(self):
        super().__init__(CompanyResearch)

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[CompanyResearch]:
        try:
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        except SQLAlchemyError as e:
            raise e
