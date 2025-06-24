from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict, Any

from app.common.base_classes.base_service import BaseService
from app.domains.admin.schemas.admin_schemas import ProductCreate, ProductUpdate
from app.domains.ppob.models.ppob import PPOBProduct
from .product import (
    ProductCrudService,
    ProductValidationService,
    ProductStatsService
)


class ProductManagementService(BaseService):
    """Facade Service untuk manajemen produk - Facade Pattern: Menggabungkan semua product services"""
    
    def __init__(self, db: Session):
        self.db = db
        self.crud_service = ProductCrudService(db)
        self.validation_service = ProductValidationService(db)
        self.stats_service = ProductStatsService(db)
    
    # CRUD Operations - delegated to ProductCrudService
    def get_products(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[PPOBProduct], int]:
        """Ambil daftar produk dengan filter"""
        return self.crud_service.get_products(skip, limit, search, category, is_active)
    
    def get_product_categories(self) -> List[str]:
        """Ambil semua kategori produk"""
        return self.crud_service.get_product_categories()
    
    def create_product(self, product_data: ProductCreate, admin_id: str) -> PPOBProduct:
        """Buat produk baru dengan validasi"""
        # Validasi data terlebih dahulu
        self.validation_service.validate_product_data(product_data)
        
        # Buat produk
        return self.crud_service.create_product(product_data, admin_id)
    
    def update_product(
        self,
        product_id: str,
        product_data: ProductUpdate,
        admin_id: str
    ) -> PPOBProduct:
        """Update produk dengan validasi"""
        # Validasi produk exists
        self.validation_service.validate_product_exists(product_id)
        
        # Update produk
        return self.crud_service.update_product(product_id, product_data, admin_id)
    
    # Statistics Operations - delegated to ProductStatsService
    def get_product_stats(self) -> Dict[str, Any]:
        """Ambil statistik produk"""
        return self.stats_service.get_product_stats()
    
    def get_category_stats(self) -> List[Dict[str, Any]]:
        """Ambil statistik per kategori"""
        return self.stats_service.get_category_stats()
    
    def get_price_distribution(self) -> Dict[str, int]:
        """Ambil distribusi harga produk"""
        return self.stats_service.get_price_distribution()
    
    # Validation Operations - delegated to ProductValidationService
    def validate_product_code_unique(self, product_code: str, exclude_id: Optional[str] = None) -> bool:
        """Validasi kode produk unik"""
        return self.validation_service.validate_product_code_unique(product_code, exclude_id)
    
    def validate_product_exists(self, product_id: str) -> PPOBProduct:
        """Validasi produk exists"""
        return self.validation_service.validate_product_exists(product_id)
