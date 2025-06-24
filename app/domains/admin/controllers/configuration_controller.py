"""
Configuration Controller - Refactored
Menggunakan composition pattern dengan controller-controller kecil
File ini sebagai facade untuk backward compatibility
"""

from fastapi import APIRouter
import logging

from .configuration.config_system_controller import ConfigSystemController
from .configuration.config_system_crud_controller import ConfigSystemCrudController
from .configuration.config_margin_controller import ConfigMarginController
from .configuration.config_discord_controller import ConfigDiscordController

logger = logging.getLogger(__name__)


class ConfigurationController:
    """
    Configuration Controller - Facade pattern
    Menggabungkan semua controller configuration kecil
    Menyediakan interface yang sama untuk backward compatibility
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_controllers()
    
    def _setup_controllers(self):
        """Setup dan gabungkan semua controller configuration"""
        try:
            # Initialize sub-controllers
            system_controller = ConfigSystemController()
            system_crud_controller = ConfigSystemCrudController()
            margin_controller = ConfigMarginController()
            discord_controller = ConfigDiscordController()
            
            # Include all routers
            self.router.include_router(system_controller.router, tags=["config-system"])
            self.router.include_router(system_crud_controller.router, tags=["config-system-crud"])
            self.router.include_router(margin_controller.router, tags=["config-margin"])
            self.router.include_router(discord_controller.router, tags=["config-discord"])
            
            logger.info("Configuration controllers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing configuration controllers: {str(e)}", exc_info=True)
            raise


# Initialize controller instance
configuration_controller = ConfigurationController()
