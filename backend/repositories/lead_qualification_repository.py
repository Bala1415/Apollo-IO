from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.models.lead_qualification import LeadQualification
from backend.repositories.base_repository import BaseRepository

class LeadQualificationRepository(BaseRepository[LeadQualification]):
    def __init__(self):
        super().__init__(LeadQualification)

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[LeadQualification]:
        try:
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        except SQLAlchemyError as e:
            raise e
