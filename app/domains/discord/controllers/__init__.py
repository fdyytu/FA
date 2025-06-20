"""
Modul ini berisi implementasi controllers untuk Discord.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.discord.controllers.discord_bot_controller_modular import router as bot_router
from app.domains.discord.controllers.discord_config_controller import router as config_router
from app.domains.discord.controllers.bot_controller import router as bot_base_router
from app.domains.discord.controllers.analytics_controller import router as analytics_router
from app.domains.discord.controllers.livestock_controller import LiveStockController
from app.domains.discord.controllers.admin_world_config_controller import AdminWorldConfigController
from app.domains.discord.controllers.user_controller import router as user_router

discord_router = APIRouter()

discord_router.include_router(bot_router, prefix="/bot", tags=["Discord Bot"])
discord_router.include_router(config_router, prefix="/config", tags=["Discord Config"])
discord_router.include_router(bot_base_router, prefix="/base-bot", tags=["Discord Bot Base"])
discord_router.include_router(analytics_router, prefix="/analytics", tags=["Discord Analytics"])
# Create instances of new controllers
livestock_controller = LiveStockController()
admin_world_config_controller = AdminWorldConfigController()

discord_router.include_router(livestock_controller.router, prefix="/livestock", tags=["Discord LiveStock"])
discord_router.include_router(admin_world_config_controller.router, prefix="/admin-world", tags=["Discord Admin World Config"])
discord_router.include_router(user_router, prefix="/user", tags=["Discord User"])

__all__ = ['discord_router']
"""
Discord Controllers Module

Berisi semua controller untuk Discord Bot yang telah dipecah berdasarkan Single Responsibility Principle:
- BotController: Manajemen Discord Bot
- UserController: Manajemen Discord User dan Wallet
- ProductController: Manajemen LiveStock dan World Configuration
- AnalyticsController: Analytics, logs, dan statistik Discord
- DiscordConfigController: Konfigurasi Discord
"""

# Updated exports with new controllers
__all__ = [
    'discord_router',
    'livestock_controller',
    'admin_world_config_controller'
]
