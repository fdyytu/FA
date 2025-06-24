"""
Dashboard Service - Refactored
Menggunakan composition pattern dengan modul-modul kecil
File ini hanya sebagai facade untuk backward compatibility
"""

from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from .dashboard.dashboard_main_service import DashboardMainService
from .dashboard.dashboard_stats_service import DashboardStatsService
from .dashboard.dashboard_activities_service import DashboardActivitiesService
from .dashboard.dashboard_system_service import DashboardSystemService

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Dashboard Service - Facade pattern
    Menyediakan interface yang sama untuk backward compatibility
    Menggunakan composition dari service-service kecil
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.main_service = DashboardMainService(db)
        self.stats_service = DashboardStatsService(db)
        self.activities_service = DashboardActivitiesService(db)
        self.system_service = DashboardSystemService(db)
    
    # Delegate methods to appropriate services
    def get_dashboard_data(self):
        """Delegate ke main service"""
        return self.main_service.get_dashboard_data()
    
    def get_dashboard_stats(self):
        """Delegate ke stats service"""
        return self.stats_service.get_dashboard_stats()
    
    def get_recent_activities(self, limit: int = 10):
        """Delegate ke activities service"""
        return self.activities_service.get_recent_activities(limit)
    
    def get_system_health(self):
        """Delegate ke system service"""
        return self.system_service.get_system_health()
    
    def get_system_alerts(self):
        """Simplified system alerts"""
        try:
            return {"alerts": [], "critical_count": 0, "warning_count": 0, "info_count": 0}
        except Exception as e:
            logger.error(f"Error getting system alerts: {e}", exc_info=True)
            return {"alerts": [], "critical_count": 0, "warning_count": 0, "info_count": 0}
