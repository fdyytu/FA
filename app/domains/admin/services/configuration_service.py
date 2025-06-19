from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.models.admin import AdminConfig
from app.domains.admin.repositories.admin_repository import AdminConfigRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import ConfigCreate, ConfigUpdate

class ConfigurationService(BaseService):
    """Service untuk manajemen konfigurasi - Single Responsibility: Configuration management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.config_repo = AdminConfigRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_config(self, config_key: str) -> Optional[AdminConfig]:
        """Ambil konfigurasi berdasarkan key"""
        return self.config_repo.get_by_key(config_key)
    
    def get_all_configs(self, skip: int = 0, limit: int = 10) -> tuple[List[AdminConfig], int]:
        """Ambil semua konfigurasi"""
        return self.config_repo.get_all_with_pagination(skip, limit)
    
    def create_config(self, config_data: ConfigCreate, admin_id: str) -> AdminConfig:
        """Buat konfigurasi baru"""
        # Check if key already exists
        if self.config_repo.get_by_key(config_data.config_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Konfigurasi dengan key tersebut sudah ada"
            )
        
        config = AdminConfig(**config_data.dict())
        created_config = self.config_repo.create(config)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="CREATE",
            resource="config",
            resource_id=created_config.id,
            new_values=json.dumps(config_data.dict())
        )
        
        return created_config
    
    def update_config(
        self, 
        config_id: str, 
        config_data: ConfigUpdate, 
        admin_id: str
    ) -> AdminConfig:
        """Update konfigurasi"""
        config = self.config_repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "config_value": config.config_value,
            "description": config.description,
            "is_active": config.is_active
        }
        
        # Update fields
        update_data = config_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        updated_config = self.config_repo.update(config)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="config",
            resource_id=config_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data)
        )
        
        return updated_config
