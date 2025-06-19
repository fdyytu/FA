from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

T = TypeVar('T', bound=DeclarativeMeta)

class BaseRepository(Generic[T]):
    """Base repository class"""
    
    def __init__(self, model: T, db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Get all records"""
        return self.db.query(self.model).offset(offset).limit(limit).all()
    
    def create(self, obj_data: Dict[str, Any]) -> T:
        """Create new record"""
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_data: Dict[str, Any]) -> Optional[T]:
        """Update record"""
        db_obj = self.get_by_id(id)
        if db_obj:
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """Delete record"""
        db_obj = self.get_by_id(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
