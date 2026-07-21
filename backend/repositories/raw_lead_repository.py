from typing import Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.models.raw_lead import RawLead
from backend.repositories.base_repository import BaseRepository

class RawLeadRepository(BaseRepository[RawLead]):
    def __init__(self):
        super().__init__(RawLead)
        
    def get_by_email(self, db: Session, email: str) -> Optional[RawLead]:
        try:
            return db.query(self.model).filter(self.model.email == email).first()
        except SQLAlchemyError as e:
            raise e
            
    def get_by_company_domain(self, db: Session, domain: str) -> Optional[RawLead]:
        try:
            return db.query(self.model).filter(self.model.company_domain == domain).first()
        except SQLAlchemyError as e:
            raise e

    def update_status(self, db: Session, lead_id: Any, status: str) -> Optional[RawLead]:
        try:
            obj = self.get_by_id(db, lead_id)
            if obj:
                obj.status = status
                db.add(obj)
                db.commit()
                db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise e
