from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.models.lead_score import LeadScore
from backend.repositories.base_repository import BaseRepository

class LeadScoreRepository(BaseRepository[LeadScore]):
    def __init__(self):
        super().__init__(LeadScore)

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[LeadScore]:
        try:
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        except SQLAlchemyError as e:
            raise e
