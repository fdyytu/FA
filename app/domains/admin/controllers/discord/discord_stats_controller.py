"""
Discord Stats Controller - Facade Pattern
Dipecah dari file besar menjadi 2 sub-controllers untuk meningkatkan maintainability

Sub-controllers:
- StatsMainController: Statistik utama Discord
- StatsAnalyticsController: Analytics dan laporan Discord
"""

from fastapi import APIRouter
import logging

from .stats import (
    stats_main_controller,
    stats_analytics_controller
)

logger = logging.getLogger(__name__)


class DiscordStatsController:
    """
    Facade Controller untuk Discord statistics
    
    Pattern: Facade Pattern - Menyediakan interface sederhana untuk sub-controllers
    Single Responsibility: Orchestrate Discord statistics operations
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        logger.info("DiscordStatsController (Facade) initialized with 2 sub-controllers")
    
    def _setup_routes(self):
        """Setup routes dengan delegation ke sub-controllers"""
        
        # Include Main Stats routes (basic statistics)
        self.router.include_router(
            stats_main_controller.router,
            tags=["Discord Stats - Main"]
        )
        
        # Include Analytics routes (advanced analytics)
        self.router.include_router(
            stats_analytics_controller.router,
            tags=["Discord Stats - Analytics"]
        )
        
        logger.info("Discord Stats Facade Pattern implemented with 2 sub-controllers")


# Create facade controller instance
discord_stats_controller = DiscordStatsController()
