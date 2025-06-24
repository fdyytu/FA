"""
Repository untuk margin PPOB
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.common.logging.admin_logger import admin_logger
from app.domains.ppob.models.ppob import PPOBMarginConfig


class PPOBMarginRepository:
    """
    Repository untuk margin PPOB - Single Responsibility: Data access untuk margin
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("PPOBMarginRepository initialized")
    
    def get_by_category(self, category: str) -> List[PPOBMarginConfig]:
        """Ambil margin berdasarkan kategori"""
        try:
            admin_logger.info(f"Mencari margin untuk kategori: {category}")
            result = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.category == category,
                PPOBMarginConfig.is_active == True
            ).all()
            admin_logger.info(f"Ditemukan {len(result)} margin untuk kategori: {category}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari margin untuk kategori: {category}", e)
            raise
    
    def get_by_product_code(self, product_code: str) -> Optional[PPOBMarginConfig]:
        """Ambil margin berdasarkan kode produk"""
        try:
            admin_logger.info(f"Mencari margin untuk product code: {product_code}")
            result = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.product_code == product_code,
                PPOBMarginConfig.is_active == True
            ).first()
            if result:
                admin_logger.info(f"Margin ditemukan untuk product code: {product_code}")
            else:
                admin_logger.warning(f"Margin tidak ditemukan untuk product code: {product_code}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari margin untuk product code: {product_code}", e)
            raise
    
    def get_global_margin(self, category: str) -> Optional[PPOBMarginConfig]:
        """Ambil margin global untuk kategori"""
        try:
            admin_logger.info(f"Mencari margin global untuk kategori: {category}")
            result = self.db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.category == category,
                PPOBMarginConfig.product_code.is_(None),
                PPOBMarginConfig.is_active == True
            ).first()
            if result:
                admin_logger.info(f"Margin global ditemukan untuk kategori: {category}")
            else:
                admin_logger.warning(f"Margin global tidak ditemukan untuk kategori: {category}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari margin global untuk kategori: {category}", e)
            raise
