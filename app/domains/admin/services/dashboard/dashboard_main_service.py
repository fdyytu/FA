"""
Dashboard Main Service
Service utama yang menggabungkan semua komponen dashboard
Maksimal 50 baris per file
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import DashboardRepository
from app.domains.admin.schemas.admin_schemas import DashboardResponse, DashboardStats, TransactionStats

from .dashboard_stats_service import DashboardStatsService
from .dashboard_activities_service import DashboardActivitiesService
from .dashboard_system_service import DashboardSystemService
from .dashboard_helpers import get_transaction_trends, get_top_products, get_empty_dashboard_response

logger = logging.getLogger(__name__)


class DashboardMainService(BaseService):
    """Service utama dashboard - Composition pattern"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
        self.stats_service = DashboardStatsService(db)
        self.activities_service = DashboardActivitiesService(db)
        self.system_service = DashboardSystemService(db)
    
    def get_dashboard_data(self) -> DashboardResponse:
        """Ambil data dashboard lengkap dengan improved error handling"""
        try:
            # Get statistics
            stats_data = self.stats_service.get_dashboard_stats()
            dashboard_stats = DashboardStats(**stats_data)
            
            # Get recent transactions
            recent_transactions = self.activities_service.get_recent_transactions(10)
            
            # Get transaction trends and top products using helpers
            transaction_trends = get_transaction_trends(self.dashboard_repo, 7)
            top_products = get_top_products(self.dashboard_repo, 5)
            
            logger.info("Dashboard data retrieved successfully")
            return DashboardResponse(
                stats=dashboard_stats,
                recent_transactions=recent_transactions,
                transaction_trends=transaction_trends,
                top_products=top_products
            )
            
        except Exception as e:
            logger.error(f"Error in get_dashboard_data: {str(e)}", exc_info=True)
            return get_empty_dashboard_response()
