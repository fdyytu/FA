from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.dashboard_service import DashboardService
from app.domains.admin.schemas.admin_schemas import DashboardResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

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
            
            return DashboardResponse(**dashboard_data)
        
        @self.router.get("/stats/overview")
        async def get_overview_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik overview"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_overview_stats()
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/stats/users")
        async def get_user_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik user"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_user_statistics()
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/stats/transactions")
        async def get_transaction_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik transaksi"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_transaction_statistics()
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/stats/products")
        async def get_product_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik produk"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_product_statistics()
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/stats/revenue")
        async def get_revenue_stats(
            period: str = "monthly",
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik revenue"""
            dashboard_service = DashboardService(db)
            
            stats = dashboard_service.get_revenue_statistics(period)
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/recent-activities")
        async def get_recent_activities(
            limit: int = 10,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil aktivitas terbaru"""
            dashboard_service = DashboardService(db)
            
            activities = dashboard_service.get_recent_activities(limit)
            
            return APIResponse.success(data=activities)
        
        @self.router.get("/system-health")
        async def get_system_health(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil status kesehatan sistem"""
            dashboard_service = DashboardService(db)
            
            health = dashboard_service.get_system_health()
            
            return APIResponse.success(data=health)
        
        @self.router.get("/alerts")
        async def get_system_alerts(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil alert sistem"""
            dashboard_service = DashboardService(db)
            
            alerts = dashboard_service.get_system_alerts()
            
            return APIResponse.success(data=alerts)


# Initialize controller
dashboard_controller = DashboardController()
