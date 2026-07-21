from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.models.industry_classification import IndustryClassification
from backend.repositories.base_repository import BaseRepository

class IndustryClassificationRepository(BaseRepository[IndustryClassification]):
    def __init__(self):
        super().__init__(IndustryClassification)

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[IndustryClassification]:
        try:
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        except SQLAlchemyError as e:
            raise e
