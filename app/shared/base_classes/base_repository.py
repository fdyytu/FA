from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Base repository class yang mengimplementasikan Dependency Inversion Principle.
    Semua repository harus inherit dari class ini untuk konsistensi.
    """
    
    def __init__(self, db: Session, model_class: type):
        self.db = db
        self.model_class = model_class
    
    @abstractmethod
    def create(self, obj_data: dict) -> T:
        """Buat entitas baru"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Ambil entitas berdasarkan ID"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Ambil semua entitas dengan pagination"""
        pass
    
    @abstractmethod
    def update(self, id: Any, obj_data: dict) -> Optional[T]:
        """Update entitas"""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Hapus entitas"""
        pass
    
    def _create_instance(self, **kwargs) -> T:
        """Helper method untuk membuat instance model"""
        return self.model_class(**kwargs)
    
    def _save_and_refresh(self, instance: T) -> T:
        """Helper method untuk save dan refresh instance"""
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
