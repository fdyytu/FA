"""
Dashboard Statistics Service
Menangani semua operasi statistik dashboard
Maksimal 50 baris per file
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import DashboardRepository
from app.domains.admin.schemas.admin_schemas import DashboardStats
from app.domains.ppob.models.ppob import TransactionStatus

logger = logging.getLogger(__name__)


class DashboardStatsService(BaseService):
    """Service untuk statistik dashboard - Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik dashboard"""
        try:
            stats = self.dashboard_repo.get_dashboard_stats()
            if not stats:
                logger.warning("No stats data found, returning empty stats")
                return self._get_empty_stats()
                
            # Validate enum values
            if "status" in stats:
                if stats["status"] not in [status.value for status in TransactionStatus]:
                    logger.warning(f"Invalid status {stats['status']}, using PENDING")
                    stats["status"] = TransactionStatus.PENDING.value
            
            logger.info("Dashboard stats retrieved successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Error in DashboardStatsService.get_dashboard_stats: {str(e)}", 
                        exc_info=True)
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """Helper method untuk mendapatkan statistik kosong"""
        return {
            "total_users": 0, "active_users": 0, "total_transactions": 0,
            "total_revenue": 0, "today_transactions": 0, "today_revenue": 0,
            "pending_transactions": 0, "failed_transactions": 0
        }
