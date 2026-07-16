from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.company_profile import CompanyProfile
from repositories.base_repository import BaseRepository

class CompanyProfileRepository(BaseRepository[CompanyProfile]):
    def __init__(self):
        super().__init__(CompanyProfile)

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[CompanyProfile]:
        try:
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        except SQLAlchemyError as e:
            raise e
