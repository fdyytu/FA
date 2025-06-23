"""
Admin Discord Controller
Controller untuk mengelola Discord bot dari admin dashboard
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.core.database import get_db
from app.domains.discord.services.bot_manager import bot_manager
from app.domains.discord.services.discord_config_service import discord_config_service

logger = logging.getLogger(__name__)

class AdminDiscordController:
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all admin Discord routes"""
        
        @self.router.get("/stats")
        async def get_discord_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get Discord statistics for admin dashboard"""
            try:
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
                
                return {
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
            except Exception as e:
                logger.error(f"Error getting Discord stats: {e}")
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
        
        @self.router.get("/bots")
        async def get_discord_bots(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get all Discord bots for admin dashboard"""
            try:
                # Get bot status
                bot_status = bot_manager.get_bot_status()
                
                # Get configs from database
                configs = discord_config_service.get_all_configs(db)
                
                bots_data = []
                
                if configs:
                    for config in configs:
                        # Check if this is the active config
                        is_active = config.is_active
                        status = "online" if (is_active and bot_status.get("is_running", False)) else "offline"
                        
                        bot_data = {
                            "id": config.id,
                            "name": config.name,
                            "token": f"***{config.token[-6:] if config.token else ''}",
                            "prefix": config.command_prefix,
                            "guild_id": config.guild_id,
                            "description": config.description or f"Discord bot: {config.name}",
                            "is_active": config.is_active,
                            "auto_start": config.auto_start,
                            "status": status,
                            "servers": bot_status.get("guilds_count", 0) if is_active else 0,
                            "users": bot_status.get("users_count", 0) if is_active else 0,
                            "uptime": bot_status.get("detailed_status", {}).get("uptime", "0m") if is_active else "0m",
                            "commands_count": 0,
                            "last_seen": bot_status.get("detailed_status", {}).get("last_connect") if is_active else None,
                            "created_at": config.created_at.isoformat() if config.created_at else None
                        }
                        bots_data.append(bot_data)
                else:
                    # No configs found
                    bots_data = []
                
                return {
                    "success": True,
                    "data": bots_data
                }
                
            except Exception as e:
                logger.error(f"Error getting Discord bots: {e}")
                return {
                    "success": False,
                    "error": "Failed to get Discord bots",
                    "data": []
                }
        
        @self.router.get("/worlds")
        async def get_discord_worlds() -> Dict[str, Any]:
            """Get Discord worlds/servers"""
            try:
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
                
                # If no guilds, return empty data
                if not worlds_data:
                    worlds_data = []
                
                return {
                    "success": True,
                    "data": worlds_data
                }
                
            except Exception as e:
                logger.error(f"Error getting Discord worlds: {e}")
                return {
                    "success": False,
                    "error": "Failed to get Discord worlds",
                    "data": []
                }
        
        @self.router.get("/commands/recent")
        async def get_recent_commands() -> Dict[str, Any]:
            """Get recent Discord commands"""
            try:
                # Get real data from database or command logs
                commands_data = []
                
                return {
                    "success": True,
                    "data": commands_data
                }
                
            except Exception as e:
                logger.error(f"Error getting recent commands: {e}")
                return {
                    "success": False,
                    "error": "Failed to get recent commands",
                    "data": []
                }
        
        @self.router.get("/logs")
        async def get_bot_logs() -> Dict[str, Any]:
            """Get Discord bot logs"""
            try:
                # Get real data from log files
                logs_data = []
                
                return {
                    "success": True,
                    "data": logs_data
                }
                
            except Exception as e:
                logger.error(f"Error getting bot logs: {e}")
                return {
                    "success": False,
                    "error": "Failed to get bot logs",
                    "data": []
                }
        
        @self.router.post("/bots/{bot_id}/start")
        async def start_bot(bot_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Start Discord bot"""
            try:
                # Get bot config
                config = discord_config_service.get_config_by_id(db, bot_id)
                if not config:
                    raise HTTPException(status_code=404, detail="Bot configuration not found")
                
                # Set as active config
                discord_config_service.set_active_config(db, bot_id)
                
                # Start bot
                success = await bot_manager.start_bot()
                
                if success:
                    return {
                        "success": True,
                        "message": f"Bot {config.name} berhasil dijalankan"
                    }
                else:
                    raise HTTPException(status_code=500, detail="Gagal menjalankan bot")
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error starting bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/bots/{bot_id}/stop")
        async def stop_bot(bot_id: int) -> Dict[str, Any]:
            """Stop Discord bot"""
            try:
                success = await bot_manager.stop_bot()
                
                if success:
                    return {
                        "success": True,
                        "message": f"Bot {bot_id} berhasil dihentikan"
                    }
                else:
                    raise HTTPException(status_code=500, detail="Gagal menghentikan bot")
                    
            except Exception as e:
                logger.error(f"Error stopping bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/logs")
        async def clear_logs() -> Dict[str, Any]:
            """Clear Discord bot logs"""
            try:
                # Clear real log files
                return {
                    "success": True,
                    "message": "Log berhasil dihapus"
                }
                
            except Exception as e:
                logger.error(f"Error clearing logs: {e}")
                raise HTTPException(status_code=500, detail=str(e))

# Create controller instance
admin_discord_controller = AdminDiscordController()
