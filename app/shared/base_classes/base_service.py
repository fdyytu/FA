from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session

T = TypeVar('T')
R = TypeVar('R')  # Repository type

class BaseService(ABC, Generic[T, R]):
    """
    Base service class yang mengimplementasikan Single Responsibility Principle.
    Setiap service harus fokus pada satu domain bisnis saja.
    """
    
    def __init__(self, repository: R):
        self.repository = repository
    
    @abstractmethod
    def create(self, data: dict) -> T:
        """Buat entitas baru dengan business logic"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Ambil entitas berdasarkan ID dengan business logic"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Ambil semua entitas dengan business logic"""
        pass
    
    @abstractmethod
    def update(self, id: Any, data: dict) -> Optional[T]:
        """Update entitas dengan business logic"""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Hapus entitas dengan business logic"""
        pass
    
    def _validate_business_rules(self, data: dict) -> bool:
        """Template method untuk validasi business rules"""
        return True
    
    def _before_create(self, data: dict) -> dict:
        """Hook yang dipanggil sebelum create"""
        return data
    
    def _after_create(self, instance: T) -> T:
        """Hook yang dipanggil setelah create"""
        return instance
    
    def _before_update(self, id: Any, data: dict) -> dict:
        """Hook yang dipanggil sebelum update"""
        return data
    
    def _after_update(self, instance: T) -> T:
        """Hook yang dipanggil setelah update"""
        return instance
