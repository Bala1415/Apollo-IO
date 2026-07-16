from sqlalchemy.orm import Session
from typing import Any, Optional
from repositories.base_repo import BaseRepository
from models.leads import RawLead

class LeadRepository(BaseRepository[RawLead]):
    """
    Repository for interacting with RawLead models.
    """
    def __init__(self):
        super().__init__(RawLead)
        
    def get(self, db: Session, id: Any) -> Optional[RawLead]:
        """Override get method since RawLead's primary key is lead_id, not id."""
        return db.query(self.model).filter(self.model.lead_id == id).first()

    def delete(self, db: Session, *, id: Any) -> Optional[RawLead]:
        """Override delete method since RawLead's primary key is lead_id, not id."""
        obj = db.query(self.model).filter(self.model.lead_id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

lead_repo = LeadRepository()
