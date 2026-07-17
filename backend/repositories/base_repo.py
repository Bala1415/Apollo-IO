from typing import TypeVar, Generic, Type, Optional, List, Any, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update as sa_update, exists as sa_exists, func
from datetime import datetime, timezone
from database.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    Base generic repository providing production-ready CRUD operations.
    Supports soft deletion, bulk operations, filtering, and pagination.
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by its primary key ID, excluding soft-deleted."""
        query = db.query(self.model).filter(self.model.id == id)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.first()

    def get_by_lead_id(self, db: Session, lead_id: Any) -> Optional[ModelType]:
        """Get a record by its associated lead_id, excluding soft-deleted."""
        if hasattr(self.model, "lead_id"):
            query = db.query(self.model).filter(self.model.lead_id == lead_id)
            if hasattr(self.model, "deleted_at"):
                query = query.filter(self.model.deleted_at.is_(None))
            return query.first()
        return None

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get a list of records, excluding soft-deleted (Alias for list)."""
        return self.list(db, skip=skip, limit=limit)

    def list(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get a list of records, excluding soft-deleted."""
        query = db.query(self.model)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.offset(skip).limit(limit).all()

    def get_by_filters(self, db: Session, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get a list of records matching exact filters, excluding soft-deleted."""
        query = db.query(self.model)
        for attr, value in filters.items():
            if hasattr(self.model, attr):
                query = query.filter(getattr(self.model, attr) == value)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.offset(skip).limit(limit).all()

    def exists(self, db: Session, id: Any) -> bool:
        """Check if a record exists by ID."""
        query = db.query(self.model).filter(self.model.id == id)
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return db.query(query.exists()).scalar()

    def count(self, db: Session) -> int:
        """Count total non-deleted records."""
        query = db.query(func.count(self.model.id))
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))
        return query.scalar()

    def paginate(self, db: Session, page: int = 1, size: int = 50) -> Tuple[List[ModelType], int]:
        """Returns paginated results and total count."""
        skip = (page - 1) * size
        total = self.count(db)
        items = self.list(db, skip=skip, limit=size)
        return items, total

    def create(self, db: Session, *, obj_in: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def bulk_create(self, db: Session, *, objs_in: List[dict]) -> List[ModelType]:
        """Create multiple records at once."""
        db_objs = [self.model(**obj) for obj in objs_in]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def bulk_update(self, db: Session, *, objs_in: List[dict]) -> None:
        """Update multiple records efficiently (requires 'id' in each dict)."""
        db.execute(sa_update(self.model), objs_in)
        db.commit()

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """Hard delete a record by its primary key."""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def soft_delete(self, db: Session, *, id: Any, deleted_by: Optional[str] = None) -> Optional[ModelType]:
        """Soft delete a record by setting deleted_at."""
        obj = self.get(db, id)
        if obj and hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now(timezone.utc)
            if deleted_by and hasattr(obj, "updated_by"):
                obj.updated_by = deleted_by
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj
