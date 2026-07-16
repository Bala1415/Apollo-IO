from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.recommendation import Recommendation
from repositories.base_repository import BaseRepository

class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self):
        super().__init__(Recommendation)

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[Recommendation]:
        try:
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        except SQLAlchemyError as e:
            raise e
