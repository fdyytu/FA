from fastapi import APIRouter
from app.domains.auth.controllers.auth_controller import router as auth_router
from app.domains.ppob.controllers.ppob_controller import router as ppob_router
from app.domains.wallet.controllers.wallet_controller import router as wallet_router
from app.domains.admin.controllers.admin_controller import router as admin_router
from app.domains.discord.controllers.discord_controller import router as discord_router
from app.domains.notification.controllers.notification_controller import router as notification_router
from app.domains.file_monitor.controllers.file_monitor_controller import router as file_monitor_router

# Import remaining endpoints
from app.api.v1.endpoints import cache, health

api_router = APIRouter()

# Domain-based routes
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(ppob_router, prefix="/ppob", tags=["ppob"])
api_router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(discord_router, prefix="/discord", tags=["discord"])
api_router.include_router(notification_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(file_monitor_router, prefix="/file-monitor", tags=["file-monitor"])

# Utility endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
