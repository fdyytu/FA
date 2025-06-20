"""
Dashboard Stats Repository
Repository untuk statistik dashboard
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
import logging

from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, PPOBCategory, TransactionStatus
from app.common.base_classes.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DashboardStatsRepository(BaseRepository):
    """Repository untuk statistik dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Ambil statistik user"""
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0
            }
    
    def get_category_stats(self) -> Dict[str, Any]:
        """Ambil statistik kategori"""
        try:
            categories = self.db.query(PPOBCategory).filter(
                PPOBCategory.is_active == True
            ).all()
            
            category_stats = {}
            for category in categories:
                category_stats[category.code] = {
                    "name": category.name,
                    "total_transactions": 0,
                    "total_revenue": 0,
                    "pending_transactions": 0,
                    "failed_transactions": 0
                }
            
            return category_stats
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return {}
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """Ambil ringkasan transaksi"""
        try:
            transactions = self.db.query(PPOBTransaction).all()
            
            total_transactions = 0
            pending_transactions = 0
            failed_transactions = 0
            total_revenue = 0
            
            for tx in transactions:
                try:
                    total_transactions += 1
                    
                    if hasattr(tx, 'amount') and tx.amount:
                        total_revenue += float(tx.amount)
                    
                    if hasattr(tx, 'status'):
                        if tx.status == TransactionStatus.PENDING:
                            pending_transactions += 1
                        elif tx.status == TransactionStatus.FAILED:
                            failed_transactions += 1
                            
                except Exception as tx_error:
                    logger.warning(f"Error processing transaction {tx.id}: {tx_error}")
                    continue
            
            return {
                "total_transactions": total_transactions,
                "pending_transactions": pending_transactions,
                "failed_transactions": failed_transactions,
                "success_transactions": total_transactions - pending_transactions - failed_transactions,
                "total_revenue": total_revenue
            }
        except Exception as e:
            logger.error(f"Error getting transaction summary: {e}")
            return {
                "total_transactions": 0,
                "pending_transactions": 0,
                "failed_transactions": 0,
                "success_transactions": 0,
                "total_revenue": 0
            }
