"""
PPOB Margin Repository
Repository untuk data access PPOB margin configuration
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.domains.admin.models.admin import PPOBMarginConfig


class PPOBMarginRepository:
    """
    Repository untuk margin PPOB - Single Responsibility: Data access untuk margin
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_category(self, category: str) -> List[PPOBMarginConfig]:
        """Ambil margin berdasarkan kategori"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.category == category,
            PPOBMarginConfig.is_active == True
        ).all()
    
    def get_by_product_code(self, product_code: str) -> Optional[PPOBMarginConfig]:
        """Ambil margin berdasarkan kode produk"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.product_code == product_code,
            PPOBMarginConfig.is_active == True
        ).first()
    
    def get_global_margin(self, category: str) -> Optional[PPOBMarginConfig]:
        """Ambil margin global untuk kategori"""
        return self.db.query(PPOBMarginConfig).filter(
            PPOBMarginConfig.category == category,
            PPOBMarginConfig.product_code.is_(None),
            PPOBMarginConfig.is_active == True
        ).first()
