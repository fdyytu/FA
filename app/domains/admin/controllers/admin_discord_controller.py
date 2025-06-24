"""
Admin Discord Controller - Versi baru yang menggunakan controller yang sudah dipecah
Menggantikan admin_discord_controller.py yang besar dengan composition pattern
"""

from fastapi import APIRouter

from app.common.logging.admin_logger import admin_logger
from app.domains.admin.controllers.discord.discord_stats_controller import discord_stats_controller
from app.domains.admin.controllers.discord.discord_bots_controller import discord_bots_controller
from app.domains.admin.controllers.discord.discord_worlds_controller import discord_worlds_controller


class AdminDiscordController:
    """
    Admin Discord Controller yang menggunakan composition pattern
    Menggabungkan semua controller Discord yang sudah dipecah
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("AdminDiscordController (new) initialized dengan sub-controllers")
    
    def _setup_routes(self):
        """Setup semua Discord routes dengan menggabungkan sub-controllers"""
        
        # Include semua sub-routers
        self.router.include_router(
            discord_stats_controller.router, 
            prefix="", 
            tags=["Admin Discord Stats"]
        )
        
        self.router.include_router(
            discord_bots_controller.router, 
            prefix="", 
            tags=["Admin Discord Bots"]
        )
        
        self.router.include_router(
            discord_worlds_controller.router, 
            prefix="", 
            tags=["Admin Discord Worlds"]
        )
        
        admin_logger.info("Semua Discord routes berhasil di-setup")


# Create controller instance
admin_discord_controller = AdminDiscordController()
