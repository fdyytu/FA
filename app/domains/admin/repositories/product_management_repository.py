"""
Repository untuk manajemen produk
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple

from app.common.logging.admin_logger import admin_logger
from app.domains.ppob.models.ppob import PPOBProduct


class ProductManagementRepository:
    """
    Repository untuk manajemen produk - Single Responsibility: Data access untuk product management
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("ProductManagementRepository initialized")
    
    def get_products_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[PPOBProduct], int]:
        """Ambil produk dengan pagination dan filter"""
        try:
            admin_logger.info(f"Mengambil products dengan pagination - skip: {skip}, limit: {limit}")
            query = self.db.query(PPOBProduct)
            
            # Apply filters
            if search:
                admin_logger.info(f"Menerapkan filter search: {search}")
                query = query.filter(
                    or_(
                        PPOBProduct.product_code.ilike(f"%{search}%"),
                        PPOBProduct.product_name.ilike(f"%{search}%")
                    )
                )
            
            if category:
                admin_logger.info(f"Menerapkan filter category: {category}")
                query = query.filter(PPOBProduct.category == category)
            
            if is_active is not None:
                admin_logger.info(f"Menerapkan filter is_active: {is_active}")
                query = query.filter(PPOBProduct.is_active == str(is_active).lower())
            
            total = query.count()
            products = query.offset(skip).limit(limit).all()
            
            admin_logger.info(f"Ditemukan {len(products)} products dari total {total}")
            return products, total
            
        except Exception as e:
            admin_logger.error("Error saat mengambil products dengan pagination", e, {
                "skip": skip, "limit": limit, "search": search, 
                "category": category, "is_active": is_active
            })
            raise
    
    def get_product_categories(self) -> List[str]:
        """Ambil semua kategori produk"""
        try:
            admin_logger.info("Mengambil semua kategori produk")
            categories = self.db.query(PPOBProduct.category).distinct().all()
            result = [cat[0] for cat in categories]
            admin_logger.info(f"Ditemukan {len(result)} kategori produk")
            return result
        except Exception as e:
            admin_logger.error("Error saat mengambil kategori produk", e)
            raise
