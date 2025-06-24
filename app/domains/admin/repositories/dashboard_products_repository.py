"""
Repository untuk produk dashboard
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any

from app.common.logging.admin_logger import admin_logger
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus


class DashboardProductsRepository:
    """
    Repository untuk produk dashboard - Single Responsibility: Data access untuk dashboard products
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("DashboardProductsRepository initialized")
    
    def get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Ambil produk terpopuler"""
        try:
            admin_logger.info(f"Mengambil {limit} produk terpopuler")
            
            results = self.db.query(
                PPOBTransaction.product_code,
                PPOBTransaction.product_name,
                func.count(PPOBTransaction.id).label('transaction_count'),
                func.sum(PPOBTransaction.total_amount).label('total_amount')
            ).filter(
                PPOBTransaction.status == TransactionStatus.SUCCESS
            ).group_by(
                PPOBTransaction.product_code,
                PPOBTransaction.product_name
            ).order_by(
                desc(func.count(PPOBTransaction.id))
            ).limit(limit).all()
            
            top_products = [
                {
                    "product_code": result.product_code,
                    "product_name": result.product_name,
                    "transaction_count": result.transaction_count,
                    "total_amount": float(result.total_amount or 0)
                }
                for result in results
            ]
            
            admin_logger.info(f"Berhasil mengambil {len(top_products)} produk terpopuler")
            return top_products
            
        except Exception as e:
            admin_logger.error(f"Error saat mengambil {limit} produk terpopuler", e)
            raise
