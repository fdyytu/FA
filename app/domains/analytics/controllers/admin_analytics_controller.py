from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import logging

from app.core.database import get_db
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)

class AdminAnalyticsController:
    """
    Controller untuk admin analytics - endpoint khusus admin analytics
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk admin analytics"""
        
        @self.router.get("/products/categories")
        async def get_products_categories_analytics(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil analytics kategori produk"""
            try:
                # Mock data untuk analytics kategori produk
                categories_data = [
                    {
                        "category_id": "cat_001",
                        "category_name": "Pulsa",
                        "total_products": 25,
                        "total_sales": 1250,
                        "revenue": 12500000,
                        "growth_rate": 15.2
                    },
                    {
                        "category_id": "cat_002", 
                        "category_name": "Paket Data",
                        "total_products": 18,
                        "total_sales": 890,
                        "revenue": 8900000,
                        "growth_rate": 12.8
                    },
                    {
                        "category_id": "cat_003",
                        "category_name": "Token Listrik",
                        "total_products": 12,
                        "total_sales": 567,
                        "revenue": 5670000,
                        "growth_rate": 8.5
                    }
                ]
                
                return {
                    "success": True,
                    "data": categories_data,
                    "timestamp": "2025-01-21T05:30:41Z"
                }
                
            except Exception as e:
                logger.error(f"Error getting products categories analytics: {e}")
                return {
                    "success": False,
                    "data": [],
                    "message": f"Gagal mengambil analytics kategori produk: {str(e)}"
                }
        
        @self.router.get("/transactions/weekly")
        async def get_transactions_weekly_analytics(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil analytics transaksi mingguan"""
            try:
                # Mock data untuk analytics transaksi mingguan
                weekly_data = [
                    {
                        "week": "2025-W03",
                        "start_date": "2025-01-13",
                        "end_date": "2025-01-19",
                        "total_transactions": 450,
                        "total_amount": 45000000,
                        "completed_transactions": 420,
                        "pending_transactions": 20,
                        "failed_transactions": 10,
                        "growth_rate": 12.5
                    },
                    {
                        "week": "2025-W02",
                        "start_date": "2025-01-06", 
                        "end_date": "2025-01-12",
                        "total_transactions": 380,
                        "total_amount": 38000000,
                        "completed_transactions": 350,
                        "pending_transactions": 18,
                        "failed_transactions": 12,
                        "growth_rate": 8.2
                    }
                ]
                
                return {
                    "success": True,
                    "data": weekly_data,
                    "timestamp": "2025-01-21T05:30:41Z"
                }
                
            except Exception as e:
                logger.error(f"Error getting weekly transactions analytics: {e}")
                return {
                    "success": False,
                    "data": [],
                    "message": f"Gagal mengambil analytics transaksi mingguan: {str(e)}"
                }

# Initialize controller
admin_analytics_controller = AdminAnalyticsController()
