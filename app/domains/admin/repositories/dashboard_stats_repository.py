"""
Repository untuk statistik dashboard
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.common.logging.admin_logger import admin_logger
from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus


class DashboardStatsRepository:
    """
    Repository untuk statistik dashboard - Single Responsibility: Data access untuk dashboard stats
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("DashboardStatsRepository initialized")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik untuk dashboard"""
        try:
            admin_logger.info("Mengambil statistik dashboard")
            
            # User stats
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            
            # Transaction stats
            total_transactions = self.db.query(PPOBTransaction).count()
            pending_transactions = self.db.query(PPOBTransaction).filter(
                PPOBTransaction.status == TransactionStatus.PENDING
            ).count()
            failed_transactions = self.db.query(PPOBTransaction).filter(
                PPOBTransaction.status == TransactionStatus.FAILED
            ).count()
            
            # Revenue stats
            total_revenue = self.db.query(
                func.sum(PPOBTransaction.total_amount)
            ).filter(
                PPOBTransaction.status == TransactionStatus.SUCCESS
            ).scalar() or 0
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "total_transactions": total_transactions,
                "total_revenue": float(total_revenue),
                "pending_transactions": pending_transactions,
                "failed_transactions": failed_transactions
            }
            
            admin_logger.info("Statistik dashboard berhasil diambil", stats)
            return stats
            
        except Exception as e:
            admin_logger.error("Error saat mengambil statistik dashboard", e)
            raise
