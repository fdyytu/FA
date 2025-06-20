"""
Product Management Repository
Repository untuk data access product management operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from app.domains.ppob.models.ppob import PPOBProduct


class ProductManagementRepository:
    """
    Repository untuk manajemen produk - Single Responsibility: Data access untuk product management
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_products_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[PPOBProduct], int]:
        """Ambil produk dengan pagination dan filter"""
        query = self.db.query(PPOBProduct)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    PPOBProduct.product_code.ilike(f"%{search}%"),
                    PPOBProduct.product_name.ilike(f"%{search}%")
                )
            )
        
        if category:
            query = query.filter(PPOBProduct.category == category)
        
        if is_active is not None:
            query = query.filter(PPOBProduct.is_active == str(is_active).lower())
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    def get_product_categories(self) -> List[str]:
        """Ambil semua kategori produk"""
        categories = self.db.query(PPOBProduct.category).distinct().all()
        return [cat[0] for cat in categories]
