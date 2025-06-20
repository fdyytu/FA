"""
Dashboard Transactions Repository
Repository untuk data transaksi dashboard
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus
from app.common.base_classes.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DashboardTransactionsRepository(BaseRepository):
    """Repository untuk data transaksi dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ambil transaksi terbaru"""
        try:
            transactions = self.db.query(PPOBTransaction).order_by(
                desc(PPOBTransaction.created_at)
            ).limit(limit).all()
            
            result = []
            for tx in transactions:
                try:
                    tx_data = {
                        "id": tx.id,
                        "amount": float(tx.amount) if hasattr(tx, 'amount') and tx.amount else 0,
                        "status": tx.status.value if hasattr(tx, 'status') and tx.status else "unknown",
                        "created_at": tx.created_at.isoformat() if hasattr(tx, 'created_at') and tx.created_at else None,
                        "product_name": getattr(tx, 'product_name', 'Unknown Product'),
                        "customer_number": getattr(tx, 'customer_number', 'N/A')
                    }
                    result.append(tx_data)
                except Exception as tx_error:
                    logger.warning(f"Error processing transaction {tx.id}: {tx_error}")
                    continue
            
            return result
        except Exception as e:
            logger.error(f"Error getting recent transactions: {e}")
            return []
    
    def get_transaction_trends(self, days: int = 7) -> Dict[str, Any]:
        """Ambil trend transaksi dalam beberapa hari terakhir"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Query transaksi dalam periode
            transactions = self.db.query(PPOBTransaction).filter(
                and_(
                    PPOBTransaction.created_at >= start_date,
                    PPOBTransaction.created_at <= end_date
                )
            ).all()
            
            # Group by date
            daily_stats = {}
            for i in range(days):
                date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
                daily_stats[date] = {
                    "total_transactions": 0,
                    "total_revenue": 0,
                    "success_count": 0,
                    "failed_count": 0,
                    "pending_count": 0
                }
            
            for tx in transactions:
                try:
                    if hasattr(tx, 'created_at') and tx.created_at:
                        date_key = tx.created_at.strftime('%Y-%m-%d')
                        
                        if date_key in daily_stats:
                            daily_stats[date_key]["total_transactions"] += 1
                            
                            if hasattr(tx, 'amount') and tx.amount:
                                daily_stats[date_key]["total_revenue"] += float(tx.amount)
                            
                            if hasattr(tx, 'status'):
                                if tx.status == TransactionStatus.SUCCESS:
                                    daily_stats[date_key]["success_count"] += 1
                                elif tx.status == TransactionStatus.FAILED:
                                    daily_stats[date_key]["failed_count"] += 1
                                elif tx.status == TransactionStatus.PENDING:
                                    daily_stats[date_key]["pending_count"] += 1
                                    
                except Exception as tx_error:
                    logger.warning(f"Error processing transaction trend {tx.id}: {tx_error}")
                    continue
            
            return {
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "daily_stats": daily_stats,
                "total_period_transactions": sum(day["total_transactions"] for day in daily_stats.values()),
                "total_period_revenue": sum(day["total_revenue"] for day in daily_stats.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction trends: {e}")
            return {
                "period": "",
                "daily_stats": {},
                "total_period_transactions": 0,
                "total_period_revenue": 0
            }
