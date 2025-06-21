from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.dashboard_service import DashboardService
from app.domains.admin.schemas.admin_schemas import DashboardResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class DashboardController:
    """
    Controller untuk dashboard admin - Single Responsibility: Dashboard and statistics endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk dashboard admin"""
        
        @self.router.get("/", response_model=DashboardResponse)
        async def get_dashboard(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil data dashboard"""
            dashboard_service = DashboardService(db)
            
            dashboard_data = dashboard_service.get_dashboard_data()
            
            return dashboard_data
        
        @self.router.get("/stats/overview")
        async def get_overview_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik overview"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_overview_stats()
            
            return {"success": True, "data": stats}
        
        @self.router.get("/stats/users")
        async def get_user_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik user"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_user_statistics()
            
            return {"success": True, "data": stats}
        
        @self.router.get("/stats/transactions")
        async def get_transaction_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik transaksi"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_transaction_statistics()
            
            return {"success": True, "data": stats}
        
        @self.router.get("/stats/products")
        async def get_product_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik produk"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_product_statistics()
            
            return {"success": True, "data": stats}
        
        @self.router.get("/stats/revenue")
        async def get_revenue_stats(
            period: str = "monthly",
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik revenue"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_revenue_statistics(period)
            
            return {"success": True, "data": stats}
        
        @self.router.get("/recent-activities")
        async def get_recent_activities(
            limit: int = 10,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil aktivitas terbaru"""
            dashboard_service = DashboardService(db)
            
            activities = dashboard_service.get_recent_activities(limit)
            
            return {"success": True, "data": activities}
        
        @self.router.get("/system-health")
        async def get_system_health(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil status kesehatan sistem"""
            dashboard_service = DashboardService(db)
            
            health = dashboard_service.get_system_health()
            
            return {"success": True, "data": health}
        
        @self.router.get("/alerts")
        async def get_system_alerts(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil alert sistem"""
            dashboard_service = DashboardService(db)
            
            alerts = dashboard_service.get_system_alerts()
            
            return {"success": True, "data": alerts}


# Initialize controller
dashboard_controller = DashboardController()

# Create separate stats controller for /admin/stats endpoint
class AdminStatsController:
    """Controller khusus untuk endpoint /admin/stats"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk admin stats"""
        
        @self.router.get("/")
        async def get_admin_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik admin umum"""
            dashboard_service = DashboardService(db)
            
            try:
                # Gabungkan berbagai statistik
                overview_stats = dashboard_service.get_overview_stats()
                user_stats = dashboard_service.get_user_statistics()
                transaction_stats = dashboard_service.get_transaction_statistics()
                product_stats = dashboard_service.get_product_statistics()
                
                combined_stats = {
                    "overview": overview_stats,
                    "users": user_stats,
                    "transactions": transaction_stats,
                    "products": product_stats,
                    "timestamp": "2025-01-21T05:30:41Z"
                }
                
                return {"success": True, "data": combined_stats}
                
            except Exception as e:
                logger.error(f"Error getting admin stats: {e}")
                # Return error response instead of mock data
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve dashboard statistics: {str(e)}"
                )

# Initialize stats controller
admin_stats_controller = AdminStatsController()
