"""
Dashboard System Controller
Controller untuk endpoint sistem monitoring
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


class DashboardSystemController:
    """Controller untuk sistem monitoring - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk sistem monitoring"""
        
        @self.router.get("/system-health")
        async def get_system_health(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil status kesehatan sistem"""
            try:
                dashboard_service = DashboardService(db)
                health = dashboard_service.get_system_health()
                logger.info(f"System health checked by admin {current_admin.username}")
                return {"success": True, "data": health}
            except Exception as e:
                logger.error(f"Error getting system health: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get system health")
        
        @self.router.get("/alerts")
        async def get_system_alerts(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil alert sistem"""
            try:
                dashboard_service = DashboardService(db)
                alerts = dashboard_service.get_system_alerts()
                return {"success": True, "data": alerts}
            except Exception as e:
                logger.error(f"Error getting system alerts: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get system alerts")
