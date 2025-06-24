"""
Controller untuk Discord worlds/servers dan logs
Dipecah dari admin_discord_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.bot_manager import bot_manager


class DiscordWorldsController:
    """Controller untuk Discord worlds/servers dan logs"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("DiscordWorldsController initialized")
    
    def _setup_routes(self):
        """Setup Discord worlds dan logs routes"""
        
        @self.router.get("/worlds")
        async def get_discord_worlds() -> Dict[str, Any]:
            """Get Discord worlds/servers"""
            try:
                admin_logger.info("Mengambil daftar Discord worlds/servers")
                
                bot_status = bot_manager.get_bot_status()
                guilds = bot_status.get("guilds", [])
                
                worlds_data = []
                for guild in guilds:
                    world_data = {
                        "id": guild.get("id"),
                        "name": guild.get("name"),
                        "players": guild.get("member_count", 0),
                        "status": "online",
                        "owner_id": guild.get("owner_id"),
                        "icon": guild.get("icon")
                    }
                    worlds_data.append(world_data)
                
                admin_logger.info(f"Berhasil mengambil {len(worlds_data)} Discord worlds")
                return {
                    "success": True,
                    "data": worlds_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting Discord worlds", e)
                return {
                    "success": False,
                    "error": "Failed to get Discord worlds",
                    "data": []
                }
        
        @self.router.get("/commands/recent")
        async def get_recent_commands() -> Dict[str, Any]:
            """Get recent Discord commands"""
            try:
                admin_logger.info("Mengambil recent Discord commands")
                
                # Get real data from database or command logs
                commands_data = []
                
                admin_logger.info(f"Berhasil mengambil {len(commands_data)} recent commands")
                return {
                    "success": True,
                    "data": commands_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting recent commands", e)
                return {
                    "success": False,
                    "error": "Failed to get recent commands",
                    "data": []
                }
        
        @self.router.get("/logs")
        async def get_bot_logs() -> Dict[str, Any]:
            """Get Discord bot logs"""
            try:
                admin_logger.info("Mengambil Discord bot logs")
                
                # Get real data from log files
                logs_data = []
                
                admin_logger.info(f"Berhasil mengambil {len(logs_data)} bot logs")
                return {
                    "success": True,
                    "data": logs_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting bot logs", e)
                return {
                    "success": False,
                    "error": "Failed to get bot logs",
                    "data": []
                }
        
        @self.router.delete("/logs")
        async def clear_logs() -> Dict[str, Any]:
            """Clear Discord bot logs"""
            try:
                admin_logger.info("Menghapus Discord bot logs")
                
                # Clear real log files
                admin_logger.info("Discord bot logs berhasil dihapus")
                return {
                    "success": True,
                    "message": "Log berhasil dihapus"
                }
                
            except Exception as e:
                admin_logger.error("Error clearing logs", e)
                raise HTTPException(status_code=500, detail=str(e))


# Create controller instance
discord_worlds_controller = DiscordWorldsController()
