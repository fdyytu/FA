"""
Controller untuk Discord statistics
Dipecah dari admin_discord_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.bot_manager import bot_manager
from app.domains.discord.services.discord_config_service import discord_config_service


class DiscordStatsController:
    """Controller untuk Discord statistics"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("DiscordStatsController initialized")
    
    def _setup_routes(self):
        """Setup Discord stats routes"""
        
        @self.router.get("/stats")
        async def get_discord_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get Discord statistics for admin dashboard"""
            try:
                admin_logger.info("Mengambil Discord statistics")
                
                # Get bot status
                bot_status = bot_manager.get_bot_status()
                
                # Get active configs count
                active_configs = discord_config_service.get_all_configs(db)
                total_bots = len(active_configs) if active_configs else 0
                
                # Calculate active bots
                active_bots = 1 if bot_status.get("is_running", False) else 0
                
                # Get guild info from bot status
                guilds_count = bot_status.get("guilds_count", 0)
                users_count = bot_status.get("users_count", 0)
                
                stats = {
                    "success": True,
                    "data": {
                        "total_bots": total_bots,
                        "active_bots": active_bots,
                        "total_servers": guilds_count,
                        "total_users": users_count,
                        "discord_users": users_count,
                        "live_products": 0,
                        "commands_today": 0
                    }
                }
                
                admin_logger.info("Discord statistics berhasil diambil", stats["data"])
                return stats
                
            except Exception as e:
                admin_logger.error("Error getting Discord stats", e)
                return {
                    "success": False,
                    "error": "Failed to get Discord stats",
                    "data": {
                        "total_bots": 0,
                        "active_bots": 0,
                        "total_servers": 0,
                        "total_users": 0,
                        "discord_users": 0,
                        "live_products": 0,
                        "commands_today": 0
                    }
                }


# Create controller instance
discord_stats_controller = DiscordStatsController()
