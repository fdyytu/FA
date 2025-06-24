"""
Dashboard Controller - Refactored
Menggunakan composition pattern dengan controller-controller kecil
File ini sebagai facade untuk backward compatibility
"""

from fastapi import APIRouter
import logging

from .dashboard.dashboard_main_controller import DashboardMainController
from .dashboard.dashboard_stats_controller import DashboardStatsController
from .dashboard.dashboard_system_controller import DashboardSystemController

logger = logging.getLogger(__name__)


class DashboardController:
    """
    Dashboard Controller - Facade pattern
    Menggabungkan semua controller dashboard kecil
    Menyediakan interface yang sama untuk backward compatibility
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_controllers()
    
    def _setup_controllers(self):
        """Setup dan gabungkan semua controller dashboard"""
        try:
            # Initialize sub-controllers
            main_controller = DashboardMainController()
            stats_controller = DashboardStatsController()
            system_controller = DashboardSystemController()
            
            # Include all routers
            self.router.include_router(main_controller.router, tags=["dashboard-main"])
            self.router.include_router(stats_controller.router, tags=["dashboard-stats"])
            self.router.include_router(system_controller.router, tags=["dashboard-system"])
            
            logger.info("Dashboard controllers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing dashboard controllers: {str(e)}", exc_info=True)
            raise


# Initialize controller instance
dashboard_controller = DashboardController()
