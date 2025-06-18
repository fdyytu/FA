from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction
from app.shared.base_classes.base_repository import BaseRepository

class DashboardRepository(BaseRepository):
    """
    Repository untuk dashboard - Single Responsibility: Data access untuk dashboard
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik untuk dashboard"""
        try:
            # User stats
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            
            # Transaction stats
            total_transactions = self.db.query(PPOBTransaction).count()
            
            # Success transactions only for revenue
            success_transactions = self.db.query(PPOBTransaction).filter(
                PPOBTransaction.status == "success"
            )
            
            total_revenue = success_transactions.with_entities(
                func.coalesce(func.sum(PPOBTransaction.total_amount), 0)
            ).scalar()
            
            # Get today's stats
            today = datetime.utcnow().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            today_transactions = self.db.query(PPOBTransaction).filter(
                PPOBTransaction.created_at >= today_start
            ).count()
            
            today_revenue = self.db.query(
                func.coalesce(func.sum(PPOBTransaction.total_amount), 0)
            ).filter(
                and_(
                    PPOBTransaction.created_at >= today_start,
                    PPOBTransaction.status == "success"
                )
            ).scalar()
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_transactions": total_transactions,
                "total_revenue": float(total_revenue),
                "today_transactions": today_transactions,
                "today_revenue": float(today_revenue)
            }
            
        except Exception as e:
            # Log the error but don't expose internal error details
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting dashboard stats: {str(e)}")
            
            # Return zero values instead of mock data
            return {
                "total_users": 0,
                "active_users": 0,
                "total_transactions": 0,
                "total_revenue": 0,
                "today_transactions": 0,
                "today_revenue": 0
            }
    
    def get_recent_transactions(self, limit: int = 10) -> List[PPOBTransaction]:
        """Ambil transaksi terbaru"""
        try:
            return self.db.query(PPOBTransaction).order_by(
                desc(PPOBTransaction.created_at)
            ).limit(limit).all()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting recent transactions: {str(e)}")
            return []
    
    def get_transaction_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Ambil trend transaksi"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            results = self.db.query(
                func.date(PPOBTransaction.created_at).label('date'),
                func.count(PPOBTransaction.id).label('count'),
                func.coalesce(func.sum(PPOBTransaction.total_amount), 0).label('amount')
            ).filter(
                PPOBTransaction.created_at >= start_date
            ).group_by(
                func.date(PPOBTransaction.created_at)
            ).all()
            
            return [
                {
                    "date": str(result.date),
                    "count": result.count,
                    "amount": float(result.amount)
                }
                for result in results
            ]
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting transaction trends: {str(e)}")
            return []
