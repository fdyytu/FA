"""
Margin CRUD Service - Operasi CRUD margin
Dipecah dari margin_management_service.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import json

from app.common.base_classes.base_service import BaseService
from app.domains.ppob.models.ppob import PPOBMarginConfig
from app.domains.admin.repositories.admin_repository import PPOBMarginRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import MarginConfigCreate, MarginConfigUpdate


class MarginCrudService(BaseService):
    """Service untuk operasi CRUD margin"""
    
    def __init__(self, db: Session):
        self.db = db
        self.margin_repo = PPOBMarginRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def create_margin_config(
        self, 
        margin_data: MarginConfigCreate, 
        admin_id: str
    ) -> PPOBMarginConfig:
        """Buat konfigurasi margin baru"""
        margin_config = PPOBMarginConfig(**margin_data.dict())
        created_config = self.margin_repo.create(margin_config)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="CREATE",
            resource="margin_config",
            resource_id=created_config.id,
            new_values=json.dumps(margin_data.dict(), default=str)
        )
        
        return created_config
    
    def get_margin_config(self, config_id: str) -> PPOBMarginConfig:
        """Ambil konfigurasi margin berdasarkan ID"""
        config = self.margin_repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi margin tidak ditemukan"
            )
        return config
    
    def get_all_margin_configs(self, skip: int = 0, limit: int = 100) -> list:
        """Ambil semua konfigurasi margin"""
        return self.margin_repo.get_all(skip=skip, limit=limit)
    
    def get_margin_configs_by_category(self, category: str) -> list:
        """Ambil konfigurasi margin berdasarkan kategori"""
        return self.margin_repo.get_by_category(category)
    
    def update_margin_config(
        self,
        config_id: str,
        margin_data: MarginConfigUpdate,
        admin_id: str
    ) -> PPOBMarginConfig:
        """Update konfigurasi margin"""
        config = self.margin_repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi margin tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "margin_type": config.margin_type if config.margin_type else None,
            "margin_value": str(config.margin_value),
            "description": config.description,
            "is_active": config.is_active
        }
        
        # Update fields
        update_data = margin_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        updated_config = self.margin_repo.update(config)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="margin_config",
            resource_id=config_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data, default=str)
        )
        
        return updated_config
    
    def delete_margin_config(self, config_id: str, admin_id: str) -> bool:
        """Hapus konfigurasi margin"""
        config = self.margin_repo.get_by_id(config_id)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi margin tidak ditemukan"
            )
        
        # Store old values for audit
        old_values = {
            "margin_type": config.margin_type,
            "margin_value": str(config.margin_value),
            "description": config.description,
            "is_active": config.is_active
        }
        
        # Delete config
        success = self.margin_repo.delete(config_id)
        
        if success:
            # Log deletion
            self.audit_repo.create_log(
                admin_id=admin_id,
                action="DELETE",
                resource="margin_config",
                resource_id=config_id,
                old_values=json.dumps(old_values)
            )
        
        return success
    
    def activate_margin_config(self, config_id: str, admin_id: str) -> PPOBMarginConfig:
        """Aktifkan konfigurasi margin"""
        config = self.get_margin_config(config_id)
        
        old_active_status = config.is_active
        config.is_active = True
        updated_config = self.margin_repo.update(config)
        
        # Log activation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="ACTIVATE",
            resource="margin_config",
            resource_id=config_id,
            old_values=json.dumps({"is_active": old_active_status}),
            new_values=json.dumps({"is_active": True})
        )
        
        return updated_config
    
    def deactivate_margin_config(self, config_id: str, admin_id: str) -> PPOBMarginConfig:
        """Nonaktifkan konfigurasi margin"""
        config = self.get_margin_config(config_id)
        
        old_active_status = config.is_active
        config.is_active = False
        updated_config = self.margin_repo.update(config)
        
        # Log deactivation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="DEACTIVATE",
            resource="margin_config",
            resource_id=config_id,
            old_values=json.dumps({"is_active": old_active_status}),
            new_values=json.dumps({"is_active": False})
        )
        
        return updated_config
