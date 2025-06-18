from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, PPOBCategory, TransactionStatus
from app.shared.base_classes.base_repository import BaseRepository

logger = logging.getLogger(__name__)

class DashboardRepository(BaseRepository):
    """Repository untuk dashboard - Single Responsibility: Data access untuk dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Ambil statistik untuk dashboard"""
        try:
            # User stats
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            
            # Get category stats
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
            
            # Transaction stats with proper enum values and category breakdown
            transactions = self.db.query(PPOBTransaction).all()
            
            total_transactions = 0
            pending_transactions = 0
            failed_transactions = 0
            total_revenue = 0
            
            for tx in transactions:
                if tx.status == TransactionStatus.PENDING:
                    pending_transactions += 1
                elif tx.status == TransactionStatus.FAILED:
                    failed_transactions += 1
                elif tx.status == TransactionStatus.SUCCESS:
                    total_revenue += float(tx.total_amount or 0)
                    
                total_transactions += 1
            
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
                    PPOBTransaction.status == TransactionStatus.SUCCESS
                )
            ).scalar()
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "total_transactions": total_transactions,
                "total_revenue": float(total_revenue),
                "today_transactions": today_transactions,
                "today_revenue": float(today_revenue),
                "pending_transactions": pending_transactions,
                "failed_transactions": failed_transactions,
                "categories": category_stats
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {str(e)}")
            
            # Return zero values with empty categories
            return {
                "total_users": 0,
                "active_users": 0,
                "total_transactions": 0,
                "total_revenue": 0,
                "today_transactions": 0,
                "today_revenue": 0,
                "pending_transactions": 0,
                "failed_transactions": 0,
                "categories": {
                    "pulsa": {
                        "name": "Pulsa",
                        "total_transactions": 0,
                        "total_revenue": 0,
                        "pending_transactions": 0,
                        "failed_transactions": 0
                    },
                    "data": {
                        "name": "Paket Data",
                        "total_transactions": 0,
                        "total_revenue": 0,
                        "pending_transactions": 0,
                        "failed_transactions": 0
                    },
                    "pln": {
                        "name": "PLN",
                        "total_transactions": 0,
                        "total_revenue": 0,
                        "pending_transactions": 0,
                        "failed_transactions": 0
                    }
                }
            }
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ambil transaksi terbaru dengan informasi kategori"""
        try:
            transactions = self.db.query(PPOBTransaction).order_by(
                desc(PPOBTransaction.created_at)
            ).limit(limit).all()

            result = []
            for tx in transactions:
                try:
                    tx_data = {
                        "id": tx.id,
                        "transaction_code": tx.transaction_code,
                        "category": {
                            "id": None,
                            "name": "Unknown",
                            "code": "unknown"
                        },
                        "product_name": tx.product_name,
                        "customer_number": tx.customer_number,
                        "customer_name": tx.customer_name,
                        "amount": float(tx.amount or 0),
                        "admin_fee": float(tx.admin_fee or 0),
                        "total_amount": float(tx.total_amount or 0),
                        "status": tx.status.value if tx.status else "UNKNOWN",
                        "created_at": tx.created_at.isoformat() if tx.created_at else None,
                        "updated_at": tx.updated_at.isoformat() if tx.updated_at else None
                    }
                    result.append(tx_data)
                except Exception as e:
                    logger.error(f"Error processing transaction {tx.id}: {str(e)}")
                    continue

            return result
        except Exception as e:
            logger.error(f"Error getting recent transactions: {str(e)}")
            return []
    
    def get_transaction_trends(self, days: int = 7) -> Dict[str, Any]:
        """Ambil trend transaksi dengan breakdown per kategori"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get active categories
            categories = self.db.query(PPOBCategory).filter(
                PPOBCategory.is_active == True
            ).all()
            
            # Initialize result structure
            trends = {
                "total": [],
                "by_category": {}
            }
            
            # Initialize category trends
            for category in categories:
                trends["by_category"][category.code] = {
                    "name": category.name,
                    "data": []
                }
            
            # Get total trends
            total_results = self.db.query(
                func.date(PPOBTransaction.created_at).label('date'),
                func.count(PPOBTransaction.id).label('count'),
                func.coalesce(func.sum(PPOBTransaction.total_amount), 0).label('amount')
            ).filter(
                and_(
                    PPOBTransaction.created_at >= start_date,
                    PPOBTransaction.status == TransactionStatus.SUCCESS
                )
            ).group_by(
                func.date(PPOBTransaction.created_at)
            ).all()
            
            trends["total"] = [
                {
                    "date": str(result.date),
                    "count": result.count,
                    "amount": float(result.amount)
                }
                for result in total_results
            ]
            
            # Simplified trends without category breakdown
            trends["by_category"] = {
                "pulsa": {
                    "name": "Pulsa",
                    "data": []
                },
                "data": {
                    "name": "Paket Data",
                    "data": []
                },
                "pln": {
                    "name": "PLN",
                    "data": []
                }
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting transaction trends: {str(e)}")
            
            # Return empty trends with default categories
            return {
                "total": [],
                "by_category": {
                    "pulsa": {
                        "name": "Pulsa",
                        "data": []
                    },
                    "data": {
                        "name": "Paket Data",
                        "data": []
                    },
                    "pln": {
                        "name": "PLN",
                        "data": []
                    }
                }
            }
    
    def get_top_products(self, limit: int = 5) -> Dict[str, Any]:
        """Ambil produk terlaris dengan kategori"""
        try:
            # Get active categories
            categories = self.db.query(PPOBCategory).filter(
                PPOBCategory.is_active == True
            ).all()
            
            # Initialize result structure
            result = {
                "total": [],
                "by_category": {}
            }
            
            # Initialize category data
            for category in categories:
                result["by_category"][category.code] = {
                    "name": category.name,
                    "products": []
                }
            
            # Simplified top products without category join
            total_results = self.db.query(
                PPOBTransaction.product_code,
                PPOBTransaction.product_name,
                func.count(PPOBTransaction.id).label('total_transactions'),
                func.sum(PPOBTransaction.total_amount).label('total_amount')
            ).filter(
                PPOBTransaction.status == TransactionStatus.SUCCESS
            ).group_by(
                PPOBTransaction.product_code,
                PPOBTransaction.product_name
            ).order_by(
                desc('total_transactions')
            ).limit(limit).all()
            
            result["total"] = [
                {
                    "product_code": r.product_code,
                    "product_name": r.product_name,
                    "category": {
                        "code": "unknown",
                        "name": "Unknown"
                    },
                    "total_transactions": r.total_transactions,
                    "total_amount": float(r.total_amount or 0)
                }
                for r in total_results
            ]
            
            # Get top products per category
            for category in categories:
                category_results = self.db.query(
                    PPOBTransaction.product_code,
                    PPOBTransaction.product_name,
                    func.count(PPOBTransaction.id).label('total_transactions'),
                    func.sum(PPOBTransaction.total_amount).label('total_amount')
                ).filter(
                    and_(
                        PPOBTransaction.status == TransactionStatus.SUCCESS,
                        PPOBTransaction.category_id == category.id
                    )
                ).group_by(
                    PPOBTransaction.product_code,
                    PPOBTransaction.product_name
                ).order_by(
                    desc('total_transactions')
                ).limit(limit).all()
                
                result["by_category"][category.code]["products"] = [
                    {
                        "product_code": r.product_code,
                        "product_name": r.product_name,
                        "total_transactions": r.total_transactions,
                        "total_amount": float(r.total_amount or 0)
                    }
                    for r in category_results
                ]
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting top products: {str(e)}")
            
            # Return empty result with default categories
            return {
                "total": [],
                "by_category": {
                    "pulsa": {
                        "name": "Pulsa",
                        "products": []
                    },
                    "data": {
                        "name": "Paket Data",
                        "products": []
                    },
                    "pln": {
                        "name": "PLN",
                        "products": []
                    }
                }
            }
