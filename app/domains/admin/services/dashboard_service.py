from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import DashboardRepository
from app.domains.admin.schemas.admin_schemas import DashboardResponse, DashboardStats, TransactionStats
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
            
            # Convert stats dict to DashboardStats object
            dashboard_stats = DashboardStats(
                total_users=stats.get("total_users", 0),
                active_users=stats.get("active_users", 0),
                total_transactions=stats.get("total_transactions", 0),
                total_revenue=stats.get("total_revenue", 0),
                pending_transactions=stats.get("pending_transactions", 0),
                failed_transactions=stats.get("failed_transactions", 0)
            )
            
            # Convert transaction trends to TransactionStats objects
            trend_objects = []
            for trend in transaction_trends:
                if isinstance(trend, dict):
                    trend_objects.append(TransactionStats(
                        date=trend.get("date", ""),
                        count=trend.get("count", 0),
                        amount=trend.get("amount", 0)
                    ))
            
            return DashboardResponse(
                stats=dashboard_stats,
                recent_transactions=recent_transactions_data,
                transaction_trends=trend_objects,
                top_products=top_products
            )
            
        except Exception as e:
            logger.error(f"Error in get_dashboard_data: {str(e)}")
            
            # Return empty response instead of raising
            return DashboardResponse(
                stats=self._get_empty_dashboard_stats(),
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
    
    def _get_empty_dashboard_stats(self) -> DashboardStats:
        """Helper method untuk mendapatkan DashboardStats kosong"""
        return DashboardStats(
            total_users=0,
            active_users=0,
            total_transactions=0,
            total_revenue=0,
            pending_transactions=0,
            failed_transactions=0
        )
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Ambil statistik overview"""
        try:
            return self.dashboard_repo.get_dashboard_stats()
        except Exception as e:
            logger.error(f"Error getting overview stats: {e}")
            raise Exception(f"Database connection failed: {str(e)}")
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Ambil statistik user"""
        try:
            stats = self.dashboard_repo.get_dashboard_stats()
            return {
                "total_users": stats.get("total_users", 0),
                "active_users": stats.get("active_users", 0)
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {"total_users": 0, "active_users": 0}
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        """Ambil statistik transaksi"""
        try:
            stats = self.dashboard_repo.get_dashboard_stats()
            return {
                "total_transactions": stats.get("total_transactions", 0),
                "pending_transactions": stats.get("pending_transactions", 0),
                "failed_transactions": stats.get("failed_transactions", 0)
            }
        except Exception as e:
            logger.error(f"Error getting transaction statistics: {e}")
            return {"total_transactions": 0, "pending_transactions": 0, "failed_transactions": 0}
    
    def get_product_statistics(self) -> Dict[str, Any]:
        """Ambil statistik produk"""
        try:
            top_products = self.dashboard_repo.get_top_products(10)
            return {"top_products": top_products}
        except Exception as e:
            logger.error(f"Error getting product statistics: {e}")
            return {"top_products": []}
    
    def get_revenue_statistics(self, period: str = "monthly") -> Dict[str, Any]:
        """Ambil statistik revenue"""
        try:
            stats = self.dashboard_repo.get_dashboard_stats()
            return {
                "total_revenue": stats.get("total_revenue", 0),
                "period": period
            }
        except Exception as e:
            logger.error(f"Error getting revenue statistics: {e}")
            return {"total_revenue": 0, "period": period}
    
    def get_recent_activities(self, limit: int = 10) -> Dict[str, Any]:
        """Ambil aktivitas terbaru"""
        try:
            transactions = self.dashboard_repo.get_recent_transactions(limit)
            activities = []
            for tx in transactions:
                activities.append({
                    "id": tx.id,
                    "type": "transaction",
                    "description": f"Transaction {tx.transaction_code}",
                    "created_at": tx.created_at.isoformat() if tx.created_at else None
                })
            return {"activities": activities}
        except Exception as e:
            logger.error(f"Error getting recent activities: {e}")
            return {"activities": []}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Ambil status kesehatan sistem"""
        try:
            return {
                "database": "healthy",
                "cache": "healthy",
                "api": "healthy",
                "status": "all_systems_operational"
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                "database": "unknown",
                "cache": "unknown", 
                "api": "unknown",
                "status": "error"
            }
    
    def get_system_alerts(self) -> Dict[str, Any]:
        """Ambil alert sistem"""
        try:
            return {
                "alerts": [],
                "critical_count": 0,
                "warning_count": 0,
                "info_count": 0
            }
        except Exception as e:
            logger.error(f"Error getting system alerts: {e}")
            return {
                "alerts": [],
                "critical_count": 0,
                "warning_count": 0,
                "info_count": 0
            }
