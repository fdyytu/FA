
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.database import get_db
from app.domains.discord.services.bot_manager import bot_manager
from app.domains.discord.services.discord_config_service import discord_config_service
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse,
    DiscordConfigTest, DiscordConfigTestResult
)

class DiscordBotController:
    @staticmethod
    async def get_bot_status() -> Dict[str, Any]:
        try:
            status = bot_manager.get_bot_status()
            return {
                "success": True,
                "data": status
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def start_bot() -> Dict[str, Any]:
        try:
            if not bot_manager.is_initialized:
                success = await bot_manager.auto_initialize()
                if not success:
                    raise HTTPException(
                        status_code=400,
                        detail="Bot tidak dapat diinisialisasi. Periksa konfigurasi Discord di database atau DISCORD_TOKEN di environment."
                    )
            
            success = await bot_manager.start_bot()
            if success:
                return {
                    "success": True,
                    "message": "Discord bot berhasil dijalankan",
                    "data": bot_manager.get_bot_status()
                }
            else:
                raise HTTPException(status_code=500, detail="Gagal menjalankan bot")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def stop_bot() -> Dict[str, Any]:
        try:
            success = await bot_manager.stop_bot()
            if success:
                return {
                    "success": True,
                    "message": "Discord bot berhasil dihentikan",
                    "data": bot_manager.get_bot_status()
                }
            else:
                raise HTTPException(status_code=500, detail="Gagal menghentikan bot")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def restart_bot() -> Dict[str, Any]:
        try:
            success = await bot_manager.restart_bot()
            if success:
                return {
                    "success": True,
                    "message": "Discord bot berhasil direstart",
                    "data": bot_manager.get_bot_status()
                }
            else:
                raise HTTPException(status_code=500, detail="Gagal merestart bot")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def send_message(channel_id: int, message: str) -> Dict[str, Any]:
        try:
            if not bot_manager.is_bot_healthy():
                raise HTTPException(
                    status_code=400,
                    detail="Bot tidak aktif atau tidak sehat"
                )
            
            success = await bot_manager.send_notification(channel_id, message)
            if success:
                return {
                    "success": True,
                    "message": "Pesan berhasil dikirim",
                    "data": {
                        "channel_id": channel_id,
                        "message": message
                    }
                }
            else:
                raise HTTPException(status_code=500, detail="Gagal mengirim pesan")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def bot_health_check() -> Dict[str, Any]:
        try:
            is_healthy = bot_manager.is_bot_healthy()
            status = bot_manager.get_bot_status()
            
            return {
                "success": True,
                "data": {
                    "healthy": is_healthy,
                    "status": status,
                    "checks": {
                        "initialized": bot_manager.is_initialized,
                        "running": status.get("is_running", False),
                        "online": status.get("status") == "online",
                        "token_configured": status.get("token_configured", False)
                    }
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "healthy": False,
                    "checks": {
                        "initialized": False,
                        "running": False,
                        "online": False,
                        "token_configured": False
                    }
                }
            }
