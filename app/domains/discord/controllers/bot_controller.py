from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import (
        DiscordBot, DiscordBotConfig, DiscordBotStatus
    )
except ImportError:
    DiscordBot = DiscordBotConfig = DiscordBotStatus = None

# Try to import Discord schemas
try:
    from app.schemas.discord import (
        DiscordBotCreate, DiscordBotUpdate, DiscordBotResponse,
        DiscordBotConfigCreate, DiscordBotConfigUpdate, DiscordBotConfigResponse
    )
except ImportError:
    DiscordBotCreate = DiscordBotUpdate = DiscordBotResponse = None
    DiscordBotConfigCreate = DiscordBotConfigUpdate = DiscordBotConfigResponse = None

# Try to import Discord service
try:
    from app.services.discord_bot_service import DiscordBotService
except ImportError:
    DiscordBotService = None

# Try to import utility functions
try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

logger = logging.getLogger(__name__)


class DiscordBotController:
    """
    Controller untuk manajemen Discord Bot - Single Responsibility: Discord bot management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self.bot_service = DiscordBotService() if DiscordBotService else None
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen Discord Bot"""
        
        @self.router.post("/", response_model=dict)
        async def create_discord_bot(
            bot_data: DiscordBotCreate,
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi Discord Bot baru"""
            try:
                # Check if bot already exists for this guild
                existing_bot = db.query(DiscordBot).filter(
                    DiscordBot.guild_id == bot_data.guild_id
                ).first()
                
                if existing_bot:
                    raise HTTPException(
                        status_code=400,
                        detail="Bot sudah ada untuk guild ini"
                    )
                
                # Create new bot
                new_bot = DiscordBot(**bot_data.dict())
                db.add(new_bot)
                db.commit()
                db.refresh(new_bot)
                
                return create_success_response(
                    data=DiscordBotResponse.from_orm(new_bot),
                    message="Discord Bot berhasil dibuat"
                )
                
            except Exception as e:
                logger.error(f"Error creating Discord bot: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/", response_model=dict)
        async def get_discord_bots(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db)
        ):
            """Ambil daftar Discord Bot"""
            try:
                if not DiscordBot:
                    # Return empty response if model not available
                    return create_success_response(
                        data={
                            "bots": [],
                            "total": 0,
                            "skip": skip,
                            "limit": limit
                        }
                    )

                bots = db.query(DiscordBot).offset(skip).limit(limit).all()
                total = db.query(DiscordBot).count()
                
                # Manual conversion since schema might not be available
                bot_list = []
                for bot in bots:
                    bot_dict = {
                        "id": bot.id,
                        "name": bot.name,
                        "guild_id": bot.guild_id,
                        "status": bot.status,
                        "is_active": bot.is_active,
                        "created_at": bot.created_at.isoformat() if bot.created_at else None,
                        "updated_at": bot.updated_at.isoformat() if bot.updated_at else None
                    }
                    bot_list.append(bot_dict)
                
                return create_success_response(
                    data={
                        "bots": bot_list,
                        "total": total,
                        "skip": skip,
                        "limit": limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting Discord bots: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/{bot_id}", response_model=dict)
        async def get_discord_bot(
            bot_id: str,
            db: Session = Depends(get_db)
        ):
            """Ambil detail Discord Bot"""
            try:
                if not DiscordBot:
                    return create_error_response("Discord Bot model not available", 503)

                bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
                
                if not bot:
                    raise HTTPException(status_code=404, detail="Discord Bot tidak ditemukan")
                
                bot_dict = {
                    "id": bot.id,
                    "name": bot.name,
                    "guild_id": bot.guild_id,
                    "status": bot.status,
                    "is_active": bot.is_active,
                    "created_at": bot.created_at.isoformat() if bot.created_at else None,
                    "updated_at": bot.updated_at.isoformat() if bot.updated_at else None
                }
                
                return create_success_response(data=bot_dict)
                
            except Exception as e:
                logger.error(f"Error getting Discord bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/{bot_id}", response_model=dict)
        async def update_discord_bot(
            bot_id: str,
            bot_data: DiscordBotUpdate,
            db: Session = Depends(get_db)
        ):
            """Update Discord Bot"""
            try:
                if not DiscordBot:
                    return create_error_response("Discord Bot model not available", 503)

                bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
                
                if not bot:
                    raise HTTPException(status_code=404, detail="Discord Bot tidak ditemukan")
                
                # Update bot data
                for field, value in bot_data.dict(exclude_unset=True).items():
                    setattr(bot, field, value)
                
                db.commit()
                db.refresh(bot)
                
                return create_success_response(
                    data=DiscordBotResponse.from_orm(bot) if DiscordBotResponse else bot,
                    message="Discord Bot berhasil diupdate"
                )
                
            except Exception as e:
                logger.error(f"Error updating Discord bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/{bot_id}")
        async def delete_discord_bot(
            bot_id: str,
            db: Session = Depends(get_db)
        ):
            """Hapus Discord Bot"""
            try:
                if not DiscordBot:
                    return create_error_response("Discord Bot model not available", 503)

                bot = db.query(DiscordBot).filter(DiscordBot.id == bot_id).first()
                
                if not bot:
                    raise HTTPException(status_code=404, detail="Discord Bot tidak ditemukan")
                
                db.delete(bot)
                db.commit()
                
                return create_success_response(message="Discord Bot berhasil dihapus")
                
            except Exception as e:
                logger.error(f"Error deleting Discord bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/{bot_id}/start")
        async def start_discord_bot(
            bot_id: str,
            db: Session = Depends(get_db)
        ):
            """Start Discord Bot"""
            try:
                if self.bot_service:
                    result = self.bot_service.start_bot(bot_id)
                    return create_success_response(
                        data=result,
                        message="Discord Bot berhasil distart"
                    )
                else:
                    return create_error_response("Discord Bot service not available", 503)
                    
            except Exception as e:
                logger.error(f"Error starting Discord bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/{bot_id}/stop")
        async def stop_discord_bot(
            bot_id: str,
            db: Session = Depends(get_db)
        ):
            """Stop Discord Bot"""
            try:
                if self.bot_service:
                    result = self.bot_service.stop_bot(bot_id)
                    return create_success_response(
                        data=result,
                        message="Discord Bot berhasil distop"
                    )
                else:
                    return create_error_response("Discord Bot service not available", 503)
                    
            except Exception as e:
                logger.error(f"Error stopping Discord bot {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/{bot_id}/status")
        async def get_bot_status(
            bot_id: str,
            db: Session = Depends(get_db)
        ):
            """Ambil status Discord Bot"""
            try:
                if self.bot_service:
                    status = self.bot_service.get_bot_status(bot_id)
                    return create_success_response(data=status)
                else:
                    return create_success_response(
                        data={
                            "status": "unknown",
                            "is_running": False,
                            "message": "Bot service not available"
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Error getting Discord bot status {bot_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))


# Initialize controller
bot_controller = DiscordBotController()
