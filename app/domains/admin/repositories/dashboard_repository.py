"""
Dashboard Repository - Modular Implementation
Repository utama dashboard yang menggunakan repository terpisah
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from .dashboard_stats_repository import DashboardStatsRepository
from .dashboard_transactions_repository import DashboardTransactionsRepository
from .dashboard_products_repository import DashboardProductsRepository
from app.common.base_classes.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DashboardRepository(BaseRepository):
    """Repository utama untuk dashboard - menggunakan composition pattern"""
    
    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = DashboardStatsRepository(db)
        self.transactions_repo = DashboardTransactionsRepository(db)
        self.products_repo = DashboardProductsRepository(db)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil semua statistik untuk dashboard"""
        try:
            # Combine stats from all repositories
            user_stats = self.stats_repo.get_user_stats()
            category_stats = self.stats_repo.get_category_stats()
            transaction_summary = self.stats_repo.get_transaction_summary()
            product_stats = self.products_repo.get_product_stats()
            
            return {
                **user_stats,
                **transaction_summary,
                **product_stats,
                "category_stats": category_stats
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ambil transaksi terbaru"""
        return self.transactions_repo.get_recent_transactions(limit)
    
    def get_transaction_trends(self, days: int = 7) -> Dict[str, Any]:
        """Ambil trend transaksi"""
        return self.transactions_repo.get_transaction_trends(days)
    
    def get_top_products(self, limit: int = 5) -> Dict[str, Any]:
        """Ambil produk terlaris"""
        return self.products_repo.get_top_products(limit)
