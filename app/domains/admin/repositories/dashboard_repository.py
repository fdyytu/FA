"""
Repository gabungan untuk dashboard
Menggunakan repository yang sudah dipecah untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.common.logging.admin_logger import admin_logger
from app.domains.admin.repositories.dashboard_stats_repository import DashboardStatsRepository
from app.domains.admin.repositories.dashboard_transactions_repository import DashboardTransactionsRepository
from app.domains.admin.repositories.dashboard_products_repository import DashboardProductsRepository


class DashboardRepository:
    """
    Repository gabungan untuk dashboard - Menggunakan composition pattern
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = DashboardStatsRepository(db)
        self.transactions_repo = DashboardTransactionsRepository(db)
        self.products_repo = DashboardProductsRepository(db)
        admin_logger.info("DashboardRepository initialized dengan sub-repositories")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik untuk dashboard"""
        return self.stats_repo.get_dashboard_stats()
    
    def get_recent_transactions(self, limit: int = 10):
        """Ambil transaksi terbaru"""
        return self.transactions_repo.get_recent_transactions(limit)
    
    def get_transaction_trends(self, days: int = 7):
        """Ambil trend transaksi"""
        return self.transactions_repo.get_transaction_trends(days)
    
    def get_top_products(self, limit: int = 5):
        """Ambil produk terpopuler"""
        return self.products_repo.get_top_products(limit)
    
    def get_complete_dashboard_data(self) -> Dict[str, Any]:
        """Ambil semua data dashboard dalam satu call"""
        try:
            admin_logger.info("Mengambil complete dashboard data")
            
            data = {
                "stats": self.get_dashboard_stats(),
                "recent_transactions": self.get_recent_transactions(10),
                "transaction_trends": self.get_transaction_trends(7),
                "top_products": self.get_top_products(5)
            }
            
            admin_logger.info("Complete dashboard data berhasil diambil")
            return data
            
        except Exception as e:
            admin_logger.error("Error saat mengambil complete dashboard data", e)
            raise
