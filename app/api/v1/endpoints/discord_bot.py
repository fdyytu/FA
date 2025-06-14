"""
Discord Bot Management API Endpoints
Endpoint untuk mengelola Discord bot dari dashboard
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status")
async def get_bot_status() -> Dict[str, Any]:
    """Get Discord bot status"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
        status = bot_manager.get_bot_status()
        return {
            "success": True,
            "data": status
        }
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_bot() -> Dict[str, Any]:
    """Start Discord bot"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
        if not bot_manager.is_initialized:
            # Try to initialize first
            success = await bot_manager.initialize_from_env()
            if not success:
                raise HTTPException(
                    status_code=400, 
                    detail="Bot tidak dapat diinisialisasi. Periksa DISCORD_TOKEN."
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
        logger.error(f"Error starting bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_bot() -> Dict[str, Any]:
    """Stop Discord bot"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
        success = await bot_manager.stop_bot()
        
        if success:
            return {
                "success": True,
                "message": "Discord bot berhasil dihentikan",
                "data": bot_manager.get_bot_status()
            }
        else:
            raise HTTPException(status_code=500, detail="Gagal menghentikan bot")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restart")
async def restart_bot() -> Dict[str, Any]:
    """Restart Discord bot"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
        success = await bot_manager.restart_bot()
        
        if success:
            return {
                "success": True,
                "message": "Discord bot berhasil direstart",
                "data": bot_manager.get_bot_status()
            }
        else:
            raise HTTPException(status_code=500, detail="Gagal merestart bot")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-message")
async def send_message(channel_id: int, message: str) -> Dict[str, Any]:
    """Send message to Discord channel"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
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
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def bot_health_check() -> Dict[str, Any]:
    """Check Discord bot health"""
    try:
        from app.domains.discord.services.bot_manager import bot_manager
        
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
        logger.error(f"Error checking bot health: {e}")
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
