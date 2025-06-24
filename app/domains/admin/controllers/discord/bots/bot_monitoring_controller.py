"""
Bot Monitoring Controller - Monitoring dan status untuk Discord bots
Dipecah dari discord_bots_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.bot_manager import bot_manager
from app.domains.discord.services.discord_config_service import discord_config_service


class BotMonitoringController:
    """Controller untuk monitoring Discord bots"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("BotMonitoringController initialized")
    
    def _setup_routes(self):
        """Setup bot monitoring routes"""
        
        @self.router.get("/bots/status")
        async def get_bot_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get current bot status with detailed information"""
            try:
                admin_logger.info("Mengambil status Discord bot")
                
                # Get bot status
                bot_status = bot_manager.get_bot_status()
                
                # Get active config
                active_config = discord_config_service.get_active_config(db)
                
                status_data = {
                    "is_running": bot_status.get("is_running", False),
                    "guilds_count": bot_status.get("guilds_count", 0),
                    "users_count": bot_status.get("users_count", 0),
                    "uptime": bot_status.get("detailed_status", {}).get("uptime", "0m"),
                    "last_connect": bot_status.get("detailed_status", {}).get("last_connect"),
                    "active_config": {
                        "id": active_config.id if active_config else None,
                        "name": active_config.name if active_config else None,
                        "prefix": active_config.command_prefix if active_config else None
                    } if active_config else None
                }
                
                admin_logger.info(f"Status bot: {'Online' if status_data['is_running'] else 'Offline'}")
                return {
                    "success": True,
                    "data": status_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting bot status", e)
                return {
                    "success": False,
                    "error": "Failed to get bot status",
                    "data": {
                        "is_running": False,
                        "guilds_count": 0,
                        "users_count": 0,
                        "uptime": "0m",
                        "last_connect": None,
                        "active_config": None
                    }
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
        
        @self.router.post("/bots/restart")
        async def restart_bot(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Restart Discord bot"""
            try:
                admin_logger.info("Merestart Discord bot")
                
                # Stop bot first
                await bot_manager.stop_bot()
                
                # Start bot again
                success = await bot_manager.start_bot()
                
                if success:
                    admin_logger.info("Bot berhasil direstart")
                    return {
                        "success": True,
                        "message": "Bot berhasil direstart"
                    }
                else:
                    admin_logger.error("Gagal merestart bot")
                    raise HTTPException(status_code=500, detail="Gagal merestart bot")
                    
            except Exception as e:
                admin_logger.error("Error restarting bot", e)
                raise HTTPException(status_code=500, detail=str(e))


# Create controller instance
bot_monitoring_controller = BotMonitoringController()
