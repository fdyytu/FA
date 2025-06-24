"""
Repository untuk transaksi dashboard
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.common.logging.admin_logger import admin_logger
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus


class DashboardTransactionsRepository:
    """
    Repository untuk transaksi dashboard - Single Responsibility: Data access untuk dashboard transactions
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("DashboardTransactionsRepository initialized")
    
    def get_recent_transactions(self, limit: int = 10) -> List[PPOBTransaction]:
        """Ambil transaksi terbaru"""
        try:
            admin_logger.info(f"Mengambil {limit} transaksi terbaru")
            result = self.db.query(PPOBTransaction).order_by(
                desc(PPOBTransaction.created_at)
            ).limit(limit).all()
            admin_logger.info(f"Berhasil mengambil {len(result)} transaksi terbaru")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mengambil {limit} transaksi terbaru", e)
            raise
    
    def get_transaction_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Ambil trend transaksi"""
        try:
            admin_logger.info(f"Mengambil trend transaksi untuk {days} hari terakhir")
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
            
            trends = [
                {
                    "date": str(result.date),
                    "count": result.count,
                    "amount": float(result.amount or 0)
                }
                for result in results
            ]
            
            admin_logger.info(f"Berhasil mengambil trend transaksi untuk {len(trends)} hari")
            return trends
            
        except Exception as e:
            admin_logger.error(f"Error saat mengambil trend transaksi untuk {days} hari", e)
            raise
