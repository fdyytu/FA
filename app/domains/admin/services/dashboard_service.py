from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import DashboardRepository
from app.domains.admin.schemas.admin_schemas import DashboardResponse
from app.domains.ppob.models.ppob import TransactionStatus

logger = logging.getLogger(__name__)

class DashboardService(BaseService):
    """Service untuk dashboard - Single Responsibility: Dashboard data aggregation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
    
    def get_dashboard_data(self) -> DashboardResponse:
        """Ambil data dashboard lengkap"""
        try:
            # Get statistics
            stats = self.dashboard_repo.get_dashboard_stats()
            
            # Get recent transactions
            recent_transactions = self.dashboard_repo.get_recent_transactions(10)
            recent_transactions_data = []
            
            for tx in recent_transactions:
                try:
                    tx_data = {
                        "id": tx.id,
                        "transaction_code": tx.transaction_code,
                        "product_name": tx.product_name,
                        "amount": float(tx.total_amount) if tx.total_amount else 0,
                        "status": tx.status.value if hasattr(tx, 'status') and tx.status else "UNKNOWN",
                        "created_at": tx.created_at.isoformat() if tx.created_at else None
                    }
                    recent_transactions_data.append(tx_data)
                except Exception as e:
                    logger.error(f"Error processing transaction {tx.id}: {str(e)}")
                    continue
            
            # Get transaction trends with error handling
            try:
                transaction_trends = self.dashboard_repo.get_transaction_trends(7)
            except Exception as e:
                logger.error(f"Error getting transaction trends: {str(e)}")
                transaction_trends = []
            
            # Get top products with error handling
            try:
                top_products = self.dashboard_repo.get_top_products(5)
            except Exception as e:
                logger.error(f"Error getting top products: {str(e)}")
                top_products = []
            
            return DashboardResponse(
                stats=stats,
                recent_transactions=recent_transactions_data,
                transaction_trends=transaction_trends,
                top_products=top_products
            )
            
        except Exception as e:
            logger.error(f"Error in get_dashboard_data: {str(e)}")
            
            # Return empty response instead of raising
            return DashboardResponse(
                stats=self._get_empty_stats(),
                recent_transactions=[],
                transaction_trends=[],
                top_products=[]
            )
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik dashboard"""
        try:
            stats = self.dashboard_repo.get_dashboard_stats()
            if not stats:
                raise ValueError("Invalid stats data")
                
            # Validate enum values
            if "status" in stats:
                if stats["status"] not in [status.value for status in TransactionStatus]:
                    stats["status"] = TransactionStatus.PENDING.value
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in DashboardService.get_dashboard_stats: {str(e)}")
            return self._get_empty_stats()
    
    def _get_empty_stats(self) -> Dict[str, Any]:
        """Helper method untuk mendapatkan statistik kosong"""
        return {
            "total_users": 0,
            "active_users": 0,
            "total_transactions": 0,
            "total_revenue": 0,
            "today_transactions": 0,
            "today_revenue": 0,
            "pending_transactions": 0,
            "failed_transactions": 0
        }
