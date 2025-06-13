"""
Base Repository untuk implementasi Repository Pattern
Single Responsibility: Hanya menangani data access layer
DRY Principle: Reusable base functionality untuk semua repositories
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func
from pydantic import BaseModel
from app.core.interfaces import IRepository
from app.core.database import get_db
from app.core.constants import DatabaseConstants
import logging

logger = logging.getLogger(__name__)

# Type variables
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(IRepository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository dengan implementasi CRUD operations
    Menggunakan Generic untuk type safety
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Buat record baru di database
        
        Args:
            obj_in: Schema untuk create operation
            
        Returns:
            Created model instance
            
        Raises:
            SQLAlchemyError: Jika terjadi error database
        """
        try:
            # Convert pydantic model ke dict
            obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
            
            # Buat instance model
            db_obj = self.model(**obj_data)
            
            # Simpan ke database
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Created {self.model.__name__} with ID: {getattr(db_obj, 'id', 'N/A')}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def get(self, id: Any) -> Optional[ModelType]:
        """
        Ambil record berdasarkan ID
        
        Args:
            id: Primary key value
            
        Returns:
            Model instance atau None jika tidak ditemukan
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} with ID {id}: {e}")
            return None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = DatabaseConstants.DEFAULT_PAGE_SIZE,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Ambil multiple records dengan pagination dan filter
        
        Args:
            skip: Offset untuk pagination
            limit: Limit untuk pagination
            filters: Dictionary filter conditions
            order_by: Field untuk sorting
            
        Returns:
            List of model instances
        """
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            if filters:
                query = self._apply_filters(query, filters)
            
            # Apply ordering
            if order_by:
                if order_by.startswith('-'):
                    # Descending order
                    field = order_by[1:]
                    if hasattr(self.model, field):
                        query = query.order_by(getattr(self.model, field).desc())
                else:
                    # Ascending order
                    if hasattr(self.model, order_by):
                        query = query.order_by(getattr(self.model, order_by))
            
            # Apply pagination
            return query.offset(skip).limit(min(limit, DatabaseConstants.MAX_PAGE_SIZE)).all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {e}")
            return []
    
    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """
        Update record yang sudah ada
        
        Args:
            db_obj: Existing model instance
            obj_in: Schema untuk update operation
            
        Returns:
            Updated model instance
            
        Raises:
            SQLAlchemyError: Jika terjadi error database
        """
        try:
            # Convert pydantic model ke dict, exclude unset values
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Update fields
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            # Commit changes
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with ID: {getattr(db_obj, 'id', 'N/A')}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    async def delete(self, id: Any) -> bool:
        """
        Hapus record berdasarkan ID
        
        Args:
            id: Primary key value
            
        Returns:
            True jika berhasil dihapus, False jika tidak ditemukan
            
        Raises:
            SQLAlchemyError: Jika terjadi error database
        """
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            
            logger.info(f"Deleted {self.model.__name__} with ID: {id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            raise
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Hitung jumlah records dengan filter
        
        Args:
            filters: Dictionary filter conditions
            
        Returns:
            Jumlah records
        """
        try:
            query = self.db.query(func.count(self.model.id))
            
            if filters:
                query = self._apply_filters(query, filters)
            
            return query.scalar() or 0
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    async def exists(self, id: Any) -> bool:
        """
        Cek apakah record dengan ID tertentu ada
        
        Args:
            id: Primary key value
            
        Returns:
            True jika ada, False jika tidak
        """
        try:
            return self.db.query(self.model.id).filter(self.model.id == id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with ID {id}: {e}")
            return False
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """
        Ambil record berdasarkan field tertentu
        
        Args:
            field: Nama field
            value: Nilai field
            
        Returns:
            Model instance atau None
        """
        try:
            if not hasattr(self.model, field):
                logger.warning(f"Field {field} not found in {self.model.__name__}")
                return None
            
            return self.db.query(self.model).filter(getattr(self.model, field) == value).first()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by {field}: {e}")
            return None
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters ke SQLAlchemy query
        
        Args:
            query: SQLAlchemy query object
            filters: Dictionary filter conditions
            
        Returns:
            Modified query object
        """
        for field, value in filters.items():
            if not hasattr(self.model, field):
                continue
            
            model_field = getattr(self.model, field)
            
            # Handle different filter types
            if isinstance(value, dict):
                # Complex filters: {'gte': 100}, {'like': '%test%'}
                for operator, filter_value in value.items():
                    if operator == 'gte':
                        query = query.filter(model_field >= filter_value)
                    elif operator == 'lte':
                        query = query.filter(model_field <= filter_value)
                    elif operator == 'gt':
                        query = query.filter(model_field > filter_value)
                    elif operator == 'lt':
                        query = query.filter(model_field < filter_value)
                    elif operator == 'like':
                        query = query.filter(model_field.like(filter_value))
                    elif operator == 'ilike':
                        query = query.filter(model_field.ilike(filter_value))
                    elif operator == 'in':
                        query = query.filter(model_field.in_(filter_value))
                    elif operator == 'not_in':
                        query = query.filter(~model_field.in_(filter_value))
            elif isinstance(value, list):
                # IN filter
                query = query.filter(model_field.in_(value))
            else:
                # Exact match
                query = query.filter(model_field == value)
        
        return query
    
    async def bulk_create(self, objects: List[CreateSchemaType]) -> List[ModelType]:
        """
        Bulk create multiple records
        
        Args:
            objects: List of create schemas
            
        Returns:
            List of created model instances
        """
        try:
            db_objects = []
            for obj_in in objects:
                obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
                db_obj = self.model(**obj_data)
                db_objects.append(db_obj)
            
            self.db.add_all(db_objects)
            self.db.commit()
            
            for db_obj in db_objects:
                self.db.refresh(db_obj)
            
            logger.info(f"Bulk created {len(db_objects)} {self.model.__name__} records")
            return db_objects
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {e}")
            raise
