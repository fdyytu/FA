"""
Dashboard Main Controller
Controller utama untuk endpoint dashboard
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.dashboard_service import DashboardService
from app.domains.admin.schemas.admin_schemas import DashboardResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class DashboardMainController:
    """Controller utama dashboard - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk dashboard utama"""
        
        @self.router.get("/", response_model=DashboardResponse)
        async def get_dashboard(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil data dashboard lengkap"""
            try:
                dashboard_service = DashboardService(db)
                dashboard_data = dashboard_service.get_dashboard_data()
                logger.info(f"Dashboard data retrieved for admin {current_admin.username}")
                return dashboard_data
            except Exception as e:
                logger.error(f"Error getting dashboard data: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve dashboard data"
                )
        
        @self.router.get("/recent-activities")
        async def get_recent_activities(
            limit: int = 10,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil aktivitas terbaru"""
            try:
                dashboard_service = DashboardService(db)
                activities = dashboard_service.get_recent_activities(limit)
                return {"success": True, "data": activities}
            except Exception as e:
                logger.error(f"Error getting activities: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get activities")
