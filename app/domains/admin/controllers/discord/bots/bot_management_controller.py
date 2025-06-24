"""
Bot Management Controller - CRUD operations untuk Discord bots
Dipecah dari discord_bots_controller.py untuk meningkatkan maintainability
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.common.logging.admin_logger import admin_logger
from app.domains.discord.services.discord_config_service import discord_config_service


class BotManagementController:
    """Controller untuk CRUD operations Discord bots"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
        admin_logger.info("BotManagementController initialized")
    
    def _setup_routes(self):
        """Setup bot management routes"""
        
        @self.router.get("/bots")
        async def get_discord_bots(db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get all Discord bots for admin dashboard"""
            try:
                admin_logger.info("Mengambil daftar Discord bots")
                
                # Get configs from database
                configs = discord_config_service.get_all_configs(db)
                
                bots_data = []
                
                if configs:
                    for config in configs:
                        bot_data = {
                            "id": config.id,
                            "name": config.name,
                            "token": f"***{config.token[-6:] if config.token else ''}",
                            "prefix": config.command_prefix,
                            "guild_id": config.guild_id,
                            "description": config.description or f"Discord bot: {config.name}",
                            "is_active": config.is_active,
                            "auto_start": config.auto_start,
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
        
        @self.router.get("/bots/{bot_id}")
        async def get_bot_details(bot_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
            """Get specific bot details"""
            try:
                admin_logger.info(f"Mengambil detail bot dengan ID: {bot_id}")
                
                config = discord_config_service.get_config_by_id(db, bot_id)
                if not config:
                    admin_logger.warning(f"Bot configuration tidak ditemukan untuk ID: {bot_id}")
                    raise HTTPException(status_code=404, detail="Bot configuration not found")
                
                bot_data = {
                    "id": config.id,
                    "name": config.name,
                    "token": f"***{config.token[-6:] if config.token else ''}",
                    "prefix": config.command_prefix,
                    "guild_id": config.guild_id,
                    "description": config.description,
                    "is_active": config.is_active,
                    "auto_start": config.auto_start,
                    "created_at": config.created_at.isoformat() if config.created_at else None,
                    "updated_at": config.updated_at.isoformat() if config.updated_at else None
                }
                
                admin_logger.info(f"Berhasil mengambil detail bot {config.name}")
                return {
                    "success": True,
                    "data": bot_data
                }
                
            except HTTPException:
                raise
            except Exception as e:
                admin_logger.error(f"Error getting bot details {bot_id}", e)
                raise HTTPException(status_code=500, detail=str(e))


# Create controller instance
bot_management_controller = BotManagementController()
