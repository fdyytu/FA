"""
Discord Bots Controller - Facade Pattern
Dipecah dari file besar menjadi 3 sub-controllers untuk meningkatkan maintainability

Sub-controllers:
- BotManagementController: CRUD operations untuk Discord bots
- BotConfigController: Konfigurasi Discord bots  
- BotMonitoringController: Monitoring dan status Discord bots
"""

from fastapi import APIRouter
import logging

from .bots import (
    bot_management_controller,
    bot_config_controller,
    bot_monitoring_controller
)

logger = logging.getLogger(__name__)


class DiscordBotsController:
    """
    Facade Controller untuk Discord bots management
    
    Pattern: Facade Pattern - Menyediakan interface sederhana untuk sub-controllers
    Single Responsibility: Orchestrate Discord bot operations
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        logger.info("DiscordBotsController (Facade) initialized with 3 sub-controllers")
    
    def _setup_routes(self):
        """Setup routes dengan delegation ke sub-controllers"""
        
        # Include Bot Management routes (CRUD operations)
        self.router.include_router(
            bot_management_controller.router,
            tags=["Discord Bots - Management"]
        )
        
        # Include Bot Config routes (configuration)
        self.router.include_router(
            bot_config_controller.router,
            tags=["Discord Bots - Config"]
        )
        
        # Include Bot Monitoring routes (status, start/stop)
        self.router.include_router(
            bot_monitoring_controller.router,
            tags=["Discord Bots - Monitoring"]
        )
        
        logger.info("Discord Bots Facade Pattern implemented with 3 sub-controllers")


# Create facade controller instance
discord_bots_controller = DiscordBotsController()
