"""
Dashboard Stats Controller
Controller untuk endpoint statistik dashboard
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.dashboard_service import DashboardService
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class DashboardStatsController:
    """Controller untuk statistik dashboard - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk statistik dashboard"""
        
        @self.router.get("/stats/overview")
        async def get_overview_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik overview"""
            try:
                dashboard_service = DashboardService(db)
                stats = dashboard_service.get_dashboard_stats()
                return {"success": True, "data": stats}
            except Exception as e:
                logger.error(f"Error getting overview stats: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get overview stats")
        
        @self.router.get("/stats/revenue")
        async def get_revenue_stats(
            period: str = "monthly",
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik revenue"""
            try:
                dashboard_service = DashboardService(db)
                stats = {"total_revenue": 0, "period": period}  # Simplified
                return {"success": True, "data": stats}
            except Exception as e:
                logger.error(f"Error getting revenue stats: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get revenue stats")
