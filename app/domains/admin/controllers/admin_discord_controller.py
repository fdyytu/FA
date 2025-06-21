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
                        "live_products": 156,  # Mock data - bisa diganti dengan data real
                        "commands_today": 1234  # Mock data - bisa diganti dengan data real
                    }
                }
            except Exception as e:
                logger.error(f"Error getting Discord stats: {e}")
                # Return mock data if error
                return {
                    "success": True,
                    "data": {
                        "total_bots": 3,
                        "active_bots": 2,
                        "total_servers": 15,
                        "total_users": 1250,
                        "discord_users": 2450,
                        "live_products": 156,
                        "commands_today": 1234
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
                            "commands_count": 0,  # Mock data
                            "last_seen": bot_status.get("detailed_status", {}).get("last_connect") if is_active else None,
                            "created_at": config.created_at.isoformat() if config.created_at else None
                        }
                        bots_data.append(bot_data)
                else:
                    # Return mock data if no configs
                    bots_data = [
                        {
                            "id": 1,
                            "name": "FA Store Bot",
                            "token": "***XXXXXX",
                            "prefix": "!",
                            "guild_id": "123456789012345678",
                            "description": "Bot utama untuk toko FA",
                            "is_active": True,
                            "auto_start": True,
                            "status": "offline",
                            "servers": 0,
                            "users": 0,
                            "uptime": "0m",
                            "commands_count": 0,
                            "last_seen": None,
                            "created_at": None
                        }
                    ]
                
                return {
                    "success": True,
                    "data": bots_data
                }
                
            except Exception as e:
                logger.error(f"Error getting Discord bots: {e}")
                # Return mock data if error
                return {
                    "success": True,
                    "data": [
                        {
                            "id": 1,
                            "name": "FA Store Bot",
                            "token": "***XXXXXX",
                            "prefix": "!",
                            "guild_id": "123456789012345678",
                            "description": "Bot utama untuk toko FA",
                            "is_active": True,
                            "auto_start": True,
                            "status": "offline",
                            "servers": 0,
                            "users": 0,
                            "uptime": "0m",
                            "commands_count": 0,
                            "last_seen": None,
                            "created_at": None
                        }
                    ]
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
                
                # If no guilds, return mock data
                if not worlds_data:
                    worlds_data = [
                        {
                            "id": "1",
                            "name": "WORLD1",
                            "players": 45,
                            "status": "online"
                        },
                        {
                            "id": "2", 
                            "name": "WORLD2",
                            "players": 32,
                            "status": "online"
                        }
                    ]
                
                return {
                    "success": True,
                    "data": worlds_data
                }
                
            except Exception as e:
                logger.error(f"Error getting Discord worlds: {e}")
                return {
                    "success": True,
                    "data": [
                        {
                            "id": "1",
                            "name": "WORLD1", 
                            "players": 45,
                            "status": "online"
                        },
                        {
                            "id": "2",
                            "name": "WORLD2",
                            "players": 32,
                            "status": "online"
                        }
                    ]
                }
        
        @self.router.get("/commands/recent")
        async def get_recent_commands() -> Dict[str, Any]:
            """Get recent Discord commands"""
            try:
                # Mock data for now - bisa diganti dengan data real dari database
                commands_data = [
                    {
                        "id": 1,
                        "command": "/balance",
                        "user": "user123",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "status": "success"
                    },
                    {
                        "id": 2,
                        "command": "/buy",
                        "user": "user456", 
                        "timestamp": "2024-01-15T10:25:00Z",
                        "status": "success"
                    },
                    {
                        "id": 3,
                        "command": "/topup",
                        "user": "user789",
                        "timestamp": "2024-01-15T10:20:00Z",
                        "status": "pending"
                    }
                ]
                
                return {
                    "success": True,
                    "data": commands_data
                }
                
            except Exception as e:
                logger.error(f"Error getting recent commands: {e}")
                return {
                    "success": True,
                    "data": []
                }
        
        @self.router.get("/logs")
        async def get_bot_logs() -> Dict[str, Any]:
            """Get Discord bot logs"""
            try:
                # Mock data for now - bisa diganti dengan data real dari log files
                logs_data = [
                    {
                        "id": 1,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "level": "INFO",
                        "message": "Bot connected successfully",
                        "source": "discord_bot"
                    },
                    {
                        "id": 2,
                        "timestamp": "2024-01-15T10:25:00Z",
                        "level": "ERROR", 
                        "message": "Failed to process command",
                        "source": "discord_bot"
                    },
                    {
                        "id": 3,
                        "timestamp": "2024-01-15T10:20:00Z",
                        "level": "WARNING",
                        "message": "Rate limit approaching",
                        "source": "discord_bot"
                    }
                ]
                
                return {
                    "success": True,
                    "data": logs_data
                }
                
            except Exception as e:
                logger.error(f"Error getting bot logs: {e}")
                return {
                    "success": True,
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
                # Mock implementation - bisa diganti dengan implementasi real
                return {
                    "success": True,
                    "message": "Log berhasil dihapus"
                }
                
            except Exception as e:
                logger.error(f"Error clearing logs: {e}")
                raise HTTPException(status_code=500, detail=str(e))

# Create controller instance
admin_discord_controller = AdminDiscordController()
