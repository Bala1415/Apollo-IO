from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
from database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Base generic repository providing basic CRUD operations.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by its primary key ID (usually an integer id)."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[ModelType]:
        """Get a record by its associated lead_id."""
        if hasattr(self.model, "lead_id"):
            return db.query(self.model).filter(self.model.lead_id == lead_id).first()
        return None

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get a list of records."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Delete a record by its primary key."""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
