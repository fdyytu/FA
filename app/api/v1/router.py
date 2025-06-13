from fastapi import APIRouter
from app.api.v1.endpoints import file_monitor, health, cache, notification, discord_admin
from app.domains.auth.controllers.auth_controller import router as auth_router
from app.domains.ppob.controllers.ppob_controller import router as ppob_router
from app.domains.wallet.controllers.wallet_controller import router as wallet_router
from app.domains.admin.controllers.admin_controller import router as admin_router

api_router = APIRouter()

# Endpoints yang masih ada
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(file_monitor.router, prefix="/file-monitor", tags=["file-monitor"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(discord_admin.router, prefix="/discord", tags=["discord-admin"])

# Domain controllers yang tersedia
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(ppob_router, prefix="/ppob", tags=["ppob"])
api_router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
