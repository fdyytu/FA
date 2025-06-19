from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from decimal import Decimal
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.models.admin import PPOBMarginConfig, MarginType
from app.domains.admin.repositories.admin_repository import PPOBMarginRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import MarginConfigCreate, MarginConfigUpdate

class MarginManagementService(BaseService):
    """Service untuk manajemen margin - Single Responsibility: Margin management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.margin_repo = PPOBMarginRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def calculate_price_with_margin(
        self, 
        base_price: Decimal, 
        category: str, 
        product_code: Optional[str] = None
    ) -> Decimal:
        """Hitung harga dengan margin - KISS principle: Simple calculation"""
        # Try to get product-specific margin first
        margin_config = None
        if product_code:
            margin_config = self.margin_repo.get_by_product_code(product_code)
        
        # If no product-specific margin, get category margin
        if not margin_config:
            margin_config = self.margin_repo.get_global_margin(category)
        
        # If no margin config found, return base price
        if not margin_config:
            return base_price
        
        # Calculate margin
        if margin_config.margin_type == MarginType.PERCENTAGE:
            margin_amount = base_price * (margin_config.margin_value / 100)
        else:  # NOMINAL
            margin_amount = margin_config.margin_value
        
        return base_price + margin_amount
    
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
            "margin_type": config.margin_type.value if config.margin_type else None,
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
