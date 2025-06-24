"""
Dashboard Activities Service
Menangani aktivitas dan transaksi terbaru
Maksimal 50 baris per file
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import DashboardRepository

logger = logging.getLogger(__name__)


class DashboardActivitiesService(BaseService):
    """Service untuk aktivitas dashboard - Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ambil transaksi terbaru dengan error handling"""
        try:
            transactions = self.dashboard_repo.get_recent_transactions(limit)
            result = []
            
            for tx in transactions:
                try:
                    tx_data = {
                        "id": tx.id,
                        "transaction_code": tx.transaction_code,
                        "product_name": tx.product_name,
                        "amount": float(tx.total_amount) if tx.total_amount else 0,
                        "status": tx.status.value if hasattr(tx, 'status') and tx.status else "UNKNOWN",
                        "created_at": tx.created_at.isoformat() if tx.created_at else None
                    }
                    result.append(tx_data)
                except Exception as e:
                    logger.error(f"Error processing transaction {tx.id}: {str(e)}", exc_info=True)
                    continue
            
            logger.info(f"Retrieved {len(result)} recent transactions")
            return result
            
        except Exception as e:
            logger.error(f"Error getting recent transactions: {str(e)}", exc_info=True)
            return []
    
    def get_recent_activities(self, limit: int = 10) -> Dict[str, Any]:
        """Ambil aktivitas terbaru"""
        try:
            transactions = self.get_recent_transactions(limit)
            activities = [{"id": tx["id"], "type": "transaction", 
                         "description": f"Transaction {tx['transaction_code']}", 
                         "created_at": tx["created_at"]} for tx in transactions]
            return {"activities": activities}
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}", exc_info=True)
            return {"activities": []}
