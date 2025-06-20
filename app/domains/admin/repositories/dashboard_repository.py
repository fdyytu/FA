"""
Dashboard Repository
Repository untuk data access dashboard statistics dan analytics
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus


class DashboardRepository:
    """
    Repository untuk dashboard - Single Responsibility: Data access untuk dashboard
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik untuk dashboard"""
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
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_transactions": total_transactions,
            "total_revenue": float(total_revenue),
            "pending_transactions": pending_transactions,
            "failed_transactions": failed_transactions
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[PPOBTransaction]:
        """Ambil transaksi terbaru"""
        return self.db.query(PPOBTransaction).order_by(
            desc(PPOBTransaction.created_at)
        ).limit(limit).all()
    
    def get_transaction_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Ambil trend transaksi"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = self.db.query(
            func.date(PPOBTransaction.created_at).label('date'),
            func.count(PPOBTransaction.id).label('count'),
            func.sum(PPOBTransaction.total_amount).label('amount')
        ).filter(
            PPOBTransaction.created_at >= start_date
        ).group_by(
            func.date(PPOBTransaction.created_at)
        ).all()
        
        return [
            {
                "date": str(result.date),
                "count": result.count,
                "amount": float(result.amount or 0)
            }
            for result in results
        ]
    
    def get_top_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Ambil produk terpopuler"""
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
        
        return [
            {
                "product_code": result.product_code,
                "product_name": result.product_name,
                "transaction_count": result.transaction_count,
                "total_amount": float(result.total_amount or 0)
            }
            for result in results
        ]
