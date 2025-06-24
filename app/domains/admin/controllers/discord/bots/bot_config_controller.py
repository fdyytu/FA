"""
Bot Config Controller - Konfigurasi untuk Discord bots
Dipecah dari discord_bots_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.discord_config_service import discord_config_service
from app.domains.discord.services.bot_manager import bot_manager


class BotConfigController:
    """Controller untuk konfigurasi Discord bots"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("BotConfigController initialized")
    
    def _setup_routes(self):
        """Setup bot configuration routes"""
        
        @self.router.post("/bots/{bot_id}/activate")
        async def activate_bot_config(bot_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Activate bot configuration"""
            try:
                admin_logger.info(f"Mengaktifkan konfigurasi bot dengan ID: {bot_id}")
                
                # Get bot config
                config = discord_config_service.get_config_by_id(db, bot_id)
                if not config:
                    admin_logger.warning(f"Bot configuration tidak ditemukan untuk ID: {bot_id}")
                    raise HTTPException(status_code=404, detail="Bot configuration not found")
                
                # Set as active config
                discord_config_service.set_active_config(db, bot_id)
                
                admin_logger.info(f"Konfigurasi bot {config.name} berhasil diaktifkan")
                return {
                    "success": True,
                    "message": f"Konfigurasi bot {config.name} berhasil diaktifkan"
                }
                    
            except HTTPException:
                raise
            except Exception as e:
                admin_logger.error(f"Error activating bot config {bot_id}", e)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/bots/{bot_id}/deactivate")
        async def deactivate_bot_config(bot_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Deactivate bot configuration"""
            try:
                admin_logger.info(f"Menonaktifkan konfigurasi bot dengan ID: {bot_id}")
                
                # Get bot config
                config = discord_config_service.get_config_by_id(db, bot_id)
                if not config:
                    admin_logger.warning(f"Bot configuration tidak ditemukan untuk ID: {bot_id}")
                    raise HTTPException(status_code=404, detail="Bot configuration not found")
                
                # Deactivate config
                discord_config_service.deactivate_config(db, bot_id)
                
                admin_logger.info(f"Konfigurasi bot {config.name} berhasil dinonaktifkan")
                return {
                    "success": True,
                    "message": f"Konfigurasi bot {config.name} berhasil dinonaktifkan"
                }
                    
            except HTTPException:
                raise
            except Exception as e:
                admin_logger.error(f"Error deactivating bot config {bot_id}", e)
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/bots/active-config")
        async def get_active_config(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get currently active bot configuration"""
            try:
                admin_logger.info("Mengambil konfigurasi bot yang aktif")
                
                config = discord_config_service.get_active_config(db)
                if not config:
                    return {
                        "success": True,
                        "data": None,
                        "message": "Tidak ada konfigurasi bot yang aktif"
                    }
                
                config_data = {
                    "id": config.id,
                    "name": config.name,
                    "prefix": config.command_prefix,
                    "guild_id": config.guild_id,
                    "description": config.description,
                    "auto_start": config.auto_start,
                    "is_active": config.is_active
                }
                
                admin_logger.info(f"Konfigurasi aktif: {config.name}")
                return {
                    "success": True,
                    "data": config_data
                }
                
            except Exception as e:
                admin_logger.error("Error getting active config", e)
                raise HTTPException(status_code=500, detail=str(e))


# Create controller instance
bot_config_controller = BotConfigController()
