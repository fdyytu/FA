"""
Controller untuk Discord bots management
Dipecah dari admin_discord_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.bot_manager import bot_manager
from app.domains.discord.services.discord_config_service import discord_config_service


class DiscordBotsController:
    """Controller untuk Discord bots management"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("DiscordBotsController initialized")
    
    def _setup_routes(self):
        """Setup Discord bots routes"""
        
        @self.router.get("/bots")
        async def get_discord_bots(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get all Discord bots for admin dashboard"""
            try:
                admin_logger.info("Mengambil daftar Discord bots")
                
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
                
                admin_logger.info(f"Berhasil mengambil {len(bots_data)} Discord bots")
                return {
                    "success": True,
                    "data": bots_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting Discord bots", e)
                return {
                    "success": False,
                    "error": "Failed to get Discord bots",
                    "data": []
                }
        
        @self.router.post("/bots/{bot_id}/start")
        async def start_bot(bot_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Start Discord bot"""
            try:
                admin_logger.info(f"Memulai Discord bot dengan ID: {bot_id}")
                
                # Get bot config
                config = discord_config_service.get_config_by_id(db, bot_id)
                if not config:
                    admin_logger.warning(f"Bot configuration tidak ditemukan untuk ID: {bot_id}")
                    raise HTTPException(status_code=404, detail="Bot configuration not found")
                
                # Set as active config
                discord_config_service.set_active_config(db, bot_id)
                
                # Start bot
                success = await bot_manager.start_bot()
                
                if success:
                    admin_logger.info(f"Bot {config.name} berhasil dijalankan")
                    return {
                        "success": True,
                        "message": f"Bot {config.name} berhasil dijalankan"
                    }
                else:
                    admin_logger.error(f"Gagal menjalankan bot {config.name}")
                    raise HTTPException(status_code=500, detail="Gagal menjalankan bot")
                    
            except HTTPException:
                raise
            except Exception as e:
                admin_logger.error(f"Error starting bot {bot_id}", e)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/bots/{bot_id}/stop")
        async def stop_bot(bot_id: int) -> Dict[str, Any]:
            """Stop Discord bot"""
            try:
                admin_logger.info(f"Menghentikan Discord bot dengan ID: {bot_id}")
                
                success = await bot_manager.stop_bot()
                
                if success:
                    admin_logger.info(f"Bot {bot_id} berhasil dihentikan")
                    return {
                        "success": True,
                        "message": f"Bot {bot_id} berhasil dihentikan"
                    }
                else:
                    admin_logger.error(f"Gagal menghentikan bot {bot_id}")
                    raise HTTPException(status_code=500, detail="Gagal menghentikan bot")
                    
            except Exception as e:
                admin_logger.error(f"Error stopping bot {bot_id}", e)
                raise HTTPException(status_code=500, detail=str(e))


# Create controller instance
discord_bots_controller = DiscordBotsController()
