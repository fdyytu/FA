from fastapi import APIRouter, HTTPException

from app.domains.discord.services.bot_manager import bot_manager

router = APIRouter()

@router.get("/bot/status")
async def get_bot_status():
    try:
        status = bot_manager.get_bot_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot/start")
async def start_bot():
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

@router.post("/bot/stop")
async def stop_bot():
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

@router.post("/bot/restart")
async def restart_bot():
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

@router.post("/bot/send-message")
async def send_message(channel_id: int, message: str):
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

@router.get("/bot/health-check")
async def bot_health_check():
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
