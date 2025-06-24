"""
Margin Validation Service - Validasi margin
Dipecah dari margin_management_service.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import PPOBMarginRepository
from app.domains.admin.schemas.admin_schemas import MarginConfigCreate, MarginConfigUpdate


class MarginValidationService(BaseService):
    """Service untuk validasi margin"""
    
    def __init__(self, db: Session):
        self.db = db
        self.margin_repo = PPOBMarginRepository(db)
    
    def validate_margin_config(self, margin_data: MarginConfigCreate) -> bool:
        """Validasi konfigurasi margin"""
        # Validate margin value
        if margin_data.margin_value < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nilai margin tidak boleh negatif"
            )
        
        # Validate percentage margin
        if margin_data.margin_type == "percentage" and margin_data.margin_value > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Margin persentase tidak boleh lebih dari 100%"
            )
        
        # Check for duplicate config
        if self._check_duplicate_config(margin_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Konfigurasi margin untuk kategori/produk ini sudah ada"
            )
        
        return True
    
    def validate_margin_update(
        self, 
        config_id: str, 
        margin_data: MarginConfigUpdate
    ) -> bool:
        """Validasi update konfigurasi margin"""
        # Check if config exists
        existing_config = self.margin_repo.get_by_id(config_id)
        if not existing_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi margin tidak ditemukan"
            )
        
        # Validate margin value if provided
        if margin_data.margin_value is not None:
            if margin_data.margin_value < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nilai margin tidak boleh negatif"
                )
            
            # Check percentage limit
            margin_type = margin_data.margin_type or existing_config.margin_type
            if margin_type == "percentage" and margin_data.margin_value > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Margin persentase tidak boleh lebih dari 100%"
                )
        
        return True
    
    def validate_price_calculation(
        self,
        base_price: Decimal,
        margin_type: str,
        margin_value: Decimal
    ) -> bool:
        """Validasi kalkulasi harga"""
        if base_price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Harga dasar harus lebih dari 0"
            )
        
        if margin_value < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nilai margin tidak boleh negatif"
            )
        
        # Calculate final price
        if margin_type == "percentage":
            final_price = base_price * (1 + margin_value / 100)
        else:
            final_price = base_price + margin_value
        
        # Check if final price is reasonable
        if final_price > base_price * 10:  # More than 10x original price
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Harga final terlalu tinggi (lebih dari 10x harga dasar)"
            )
        
        return True
    
    def validate_bulk_operation(self, config_ids: list) -> bool:
        """Validasi operasi bulk"""
        if not config_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak ada konfigurasi yang dipilih"
            )
        
        if len(config_ids) > 100:  # Limit bulk operations
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maksimal 100 konfigurasi per operasi bulk"
            )
        
        # Check if all configs exist
        for config_id in config_ids:
            if not self.margin_repo.get_by_id(config_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Konfigurasi margin {config_id} tidak ditemukan"
                )
        
        return True
    
    def validate_margin_range(
        self,
        min_margin: Optional[Decimal] = None,
        max_margin: Optional[Decimal] = None
    ) -> bool:
        """Validasi range margin"""
        if min_margin is not None and min_margin < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Margin minimum tidak boleh negatif"
            )
        
        if max_margin is not None and max_margin < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Margin maksimum tidak boleh negatif"
            )
        
        if (min_margin is not None and max_margin is not None and 
            min_margin > max_margin):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Margin minimum tidak boleh lebih besar dari maksimum"
            )
        
        return True
    
    def _check_duplicate_config(self, margin_data: MarginConfigCreate) -> bool:
        """Check for duplicate margin configuration"""
        # Check by product code if provided
        if margin_data.product_code:
            existing = self.margin_repo.get_by_product_code(margin_data.product_code)
            return existing is not None
        
        # Check by category
        if margin_data.category:
            existing = self.margin_repo.get_global_margin(margin_data.category)
            return existing is not None
        
        return False
    
    def check_margin_conflicts(self, category: str, product_code: Optional[str] = None) -> list:
        """Check for margin configuration conflicts"""
        conflicts = []
        
        # Check if both category and product-specific margins exist
        category_margin = self.margin_repo.get_global_margin(category)
        if product_code:
            product_margin = self.margin_repo.get_by_product_code(product_code)
            
            if category_margin and product_margin:
                conflicts.append({
                    "type": "duplicate_config",
                    "message": f"Both category ({category}) and product-specific ({product_code}) margins exist",
                    "category_margin": category_margin.id,
                    "product_margin": product_margin.id
                })
        
        return conflicts
