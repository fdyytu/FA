"""
Margin Management Service - Facade Pattern
Dipecah dari file besar menjadi 3 sub-services untuk meningkatkan maintainability

Sub-services:
- MarginCalculationService: Kalkulasi margin
- MarginCrudService: Operasi CRUD margin
- MarginValidationService: Validasi margin
"""

from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.ppob.models.ppob import PPOBMarginConfig
from app.domains.admin.schemas.admin_schemas import MarginConfigCreate, MarginConfigUpdate

from .margin import (
    MarginCalculationService,
    MarginCrudService,
    MarginValidationService
)


class MarginManagementService(BaseService):
    """
    Facade Service untuk manajemen margin
    
    Pattern: Facade Pattern - Menyediakan interface sederhana untuk sub-services
    Single Responsibility: Orchestrate margin management operations
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.calculation_service = MarginCalculationService(db)
        self.crud_service = MarginCrudService(db)
        self.validation_service = MarginValidationService(db)
    
    # Delegation to calculation service
    def calculate_price_with_margin(
        self, 
        base_price: Decimal, 
        category: str, 
        product_code: Optional[str] = None
    ) -> Decimal:
        """Hitung harga dengan margin - KISS principle: Simple calculation"""
        return self.calculation_service.calculate_price_with_margin(
            base_price, category, product_code
        )
    
    def calculate_margin_amount(
        self,
        base_price: Decimal,
        margin_type: str,
        margin_value: Decimal
    ) -> Decimal:
        """Hitung jumlah margin berdasarkan tipe dan nilai"""
        return self.calculation_service.calculate_margin_amount(
            base_price, margin_type, margin_value
        )
    
    # Delegation to CRUD service
    def create_margin_config(
        self, 
        margin_data: MarginConfigCreate, 
        admin_id: str
    ) -> PPOBMarginConfig:
        """Buat konfigurasi margin baru"""
        # Validate first
        self.validation_service.validate_margin_config(margin_data)
        
        # Then create
        return self.crud_service.create_margin_config(margin_data, admin_id)
    
    def update_margin_config(
        self,
        config_id: str,
        margin_data: MarginConfigUpdate,
        admin_id: str
    ) -> PPOBMarginConfig:
        """Update konfigurasi margin"""
        # Validate first
        self.validation_service.validate_margin_update(config_id, margin_data)
        
        # Then update
        return self.crud_service.update_margin_config(config_id, margin_data, admin_id)
    
    def get_margin_config(self, config_id: str) -> PPOBMarginConfig:
        """Ambil konfigurasi margin berdasarkan ID"""
        return self.crud_service.get_margin_config(config_id)
    
    def get_all_margin_configs(self, skip: int = 0, limit: int = 100) -> list:
        """Ambil semua konfigurasi margin"""
        return self.crud_service.get_all_margin_configs(skip, limit)
    
    def delete_margin_config(self, config_id: str, admin_id: str) -> bool:
        """Hapus konfigurasi margin"""
        return self.crud_service.delete_margin_config(config_id, admin_id)
    
    # Delegation to validation service
    def validate_margin_config(self, margin_data: MarginConfigCreate) -> bool:
        """Validasi konfigurasi margin"""
        return self.validation_service.validate_margin_config(margin_data)
    
    def validate_price_calculation(
        self,
        base_price: Decimal,
        margin_type: str,
        margin_value: Decimal
    ) -> bool:
        """Validasi kalkulasi harga"""
        return self.validation_service.validate_price_calculation(
            base_price, margin_type, margin_value
        )
