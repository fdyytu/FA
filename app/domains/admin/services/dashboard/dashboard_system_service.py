"""
Dashboard System Service
Menangani monitoring sistem dan health check
Maksimal 50 baris per file
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.common.base_classes.base_service import BaseService

logger = logging.getLogger(__name__)


class DashboardSystemService(BaseService):
    """Service untuk monitoring sistem - Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_health(self) -> Dict[str, Any]:
        """Ambil status kesehatan sistem dengan detail logging"""
        try:
            # Check database connection
            db_status = self._check_database_health()
            
            # Check other components
            cache_status = "healthy"  # Placeholder for cache check
            api_status = "healthy"    # Placeholder for API check
            
            overall_status = "all_systems_operational" if all([
                db_status == "healthy", cache_status == "healthy", api_status == "healthy"
            ]) else "degraded"
            
            result = {
                "database": db_status,
                "cache": cache_status,
                "api": api_status,
                "status": overall_status
            }
            
            logger.info(f"System health check completed: {overall_status}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}", exc_info=True)
            return {"database": "unknown", "cache": "unknown", 
                   "api": "unknown", "status": "error"}
    
    def _check_database_health(self) -> str:
        """Check database connection health"""
        try:
            self.db.execute("SELECT 1")
            return "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "unhealthy"
