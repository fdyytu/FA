"""
Discord Worlds Controller - Facade Pattern
Dipecah dari file besar menjadi 3 sub-controllers untuk meningkatkan maintainability

Sub-controllers:
- WorldManagementController: Manajemen Discord worlds/servers
- WorldConfigController: Konfigurasi Discord worlds/servers
- WorldStatsController: Statistik dan logs Discord worlds/servers
"""

from fastapi import APIRouter
import logging

from .worlds import (
    world_management_controller,
    world_config_controller,
    world_stats_controller
)

logger = logging.getLogger(__name__)


class DiscordWorldsController:
    """
    Facade Controller untuk Discord worlds/servers management
    
    Pattern: Facade Pattern - Menyediakan interface sederhana untuk sub-controllers
    Single Responsibility: Orchestrate Discord world operations
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        logger.info("DiscordWorldsController (Facade) initialized with 3 sub-controllers")
    
    def _setup_routes(self):
        """Setup routes dengan delegation ke sub-controllers"""
        
        # Include World Management routes (CRUD operations)
        self.router.include_router(
            world_management_controller.router,
            tags=["Discord Worlds - Management"]
        )
        
        # Include World Config routes (configuration)
        self.router.include_router(
            world_config_controller.router,
            tags=["Discord Worlds - Config"]
        )
        
        # Include World Stats routes (statistics, logs)
        self.router.include_router(
            world_stats_controller.router,
            tags=["Discord Worlds - Stats"]
        )
        
        logger.info("Discord Worlds Facade Pattern implemented with 3 sub-controllers")


# Create facade controller instance
discord_worlds_controller = DiscordWorldsController()
