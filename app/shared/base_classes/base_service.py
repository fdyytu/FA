from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from app.utils.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseService(ABC):
    """Base service class yang mengimplementasikan prinsip DRY dan SOLID"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, model: Type[T], id: int) -> Optional[T]:
        """Generic method untuk mendapatkan entity berdasarkan ID"""
        try:
            return self.db.query(model).filter(model.id == id).first()
        except Exception as e:
            logger.error(f"Error getting {model.__name__} by id {id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil data: {str(e)}")
    
    def create(self, model: Type[T], data: Dict[str, Any]) -> T:
        """Generic method untuk membuat entity baru"""
        try:
            db_obj = model(**data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating {model.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat data: {str(e)}")
    
    def update(self, db_obj: T, data: Dict[str, Any]) -> T:
        """Generic method untuk update entity"""
        try:
            for field, value in data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating {type(db_obj).__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal update data: {str(e)}")
    
    def delete(self, db_obj: T) -> None:
        """Generic method untuk delete entity"""
        try:
            self.db.delete(db_obj)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting {type(db_obj).__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal hapus data: {str(e)}")
    
    def get_list(
        self, 
        model: Type[T], 
        page: int = 1, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generic method untuk mendapatkan list entity dengan pagination"""
        try:
            query = self.db.query(model)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(model, field):
                        query = query.filter(getattr(model, field) == value)
            
            # Apply ordering
            if order_by and hasattr(model, order_by):
                query = query.order_by(getattr(model, order_by))
            
            # Count total
            total = query.count()
            total_pages = (total + limit - 1) // limit
            
            # Apply pagination
            offset = (page - 1) * limit
            items = query.offset(offset).limit(limit).all()
            
            return {
                "items": items,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages
            }
            
        except Exception as e:
            logger.error(f"Error getting {model.__name__} list: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil daftar data: {str(e)}")
    
    def exists(self, model: Type[T], **kwargs) -> bool:
        """Generic method untuk cek apakah entity exists"""
        try:
            query = self.db.query(model)
            for field, value in kwargs.items():
                if hasattr(model, field):
                    query = query.filter(getattr(model, field) == value)
            
            return query.first() is not None
        except Exception as e:
            logger.error(f"Error checking {model.__name__} existence: {str(e)}")
            return False
    
    def count(self, model: Type[T], filters: Optional[Dict[str, Any]] = None) -> int:
        """Generic method untuk count entity"""
        try:
            query = self.db.query(model)
            
            if filters:
                for field, value in filters.items():
                    if hasattr(model, field):
                        query = query.filter(getattr(model, field) == value)
            
            return query.count()
        except Exception as e:
            logger.error(f"Error counting {model.__name__}: {str(e)}")
            return 0

class CacheableService(BaseService):
    """Service dengan caching capability"""
    
    def __init__(self, db: Session, cache_client=None):
        super().__init__(db)
        self.cache = cache_client
        self.cache_ttl = 300  # 5 minutes default
    
    def get_cached(self, key: str, fallback_func, ttl: Optional[int] = None):
        """Get data from cache or fallback function"""
        if not self.cache:
            return fallback_func()
        
        try:
            cached_data = self.cache.get(key)
            if cached_data:
                return cached_data
            
            data = fallback_func()
            self.cache.set(key, data, ttl or self.cache_ttl)
            return data
        except Exception as e:
            logger.warning(f"Cache error for key {key}: {str(e)}")
            return fallback_func()
    
    def invalidate_cache(self, pattern: str):
        """Invalidate cache by pattern"""
        if self.cache:
            try:
                self.cache.delete_pattern(pattern)
            except Exception as e:
                logger.warning(f"Cache invalidation error for pattern {pattern}: {str(e)}")

class AuditableService(BaseService):
    """Service dengan audit trail capability"""
    
    def __init__(self, db: Session, current_user_id: Optional[int] = None):
        super().__init__(db)
        self.current_user_id = current_user_id
    
    def create_with_audit(self, model: Type[T], data: Dict[str, Any], action: str = "CREATE") -> T:
        """Create entity dengan audit log"""
        try:
            # Add audit fields if model supports it
            if hasattr(model, 'created_by'):
                data['created_by'] = self.current_user_id
            
            db_obj = self.create(model, data)
            
            # Log audit trail
            self._log_audit(action, model.__name__, db_obj.id, data)
            
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {model.__name__} with audit: {str(e)}")
            raise
    
    def update_with_audit(self, db_obj: T, data: Dict[str, Any], action: str = "UPDATE") -> T:
        """Update entity dengan audit log"""
        try:
            # Store old values for audit
            old_values = {field: getattr(db_obj, field) for field in data.keys() if hasattr(db_obj, field)}
            
            # Add audit fields if model supports it
            if hasattr(db_obj, 'updated_by'):
                data['updated_by'] = self.current_user_id
            
            updated_obj = self.update(db_obj, data)
            
            # Log audit trail
            self._log_audit(action, type(db_obj).__name__, db_obj.id, {
                'old_values': old_values,
                'new_values': data
            })
            
            return updated_obj
        except Exception as e:
            logger.error(f"Error updating {type(db_obj).__name__} with audit: {str(e)}")
            raise
    
    def _log_audit(self, action: str, entity_type: str, entity_id: int, data: Dict[str, Any]):
        """Log audit trail"""
        try:
            # Implementasi audit logging
            # Bisa disimpan ke tabel audit_logs atau external service
            logger.info(f"AUDIT: {action} {entity_type} ID:{entity_id} by user:{self.current_user_id} data:{data}")
        except Exception as e:
            logger.error(f"Error logging audit: {str(e)}")
            # Don't raise exception for audit logging failures
