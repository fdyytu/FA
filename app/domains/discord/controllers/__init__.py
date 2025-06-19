"""
Modul ini berisi implementasi controllers untuk Discord.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.discord.controllers.discord_bot_controller_modular import router as bot_router
from app.domains.discord.controllers.discord_config_controller import router as config_router
from app.domains.discord.controllers.bot_controller import router as bot_base_router
from app.domains.discord.controllers.analytics_controller import router as analytics_router
from app.domains.discord.controllers.product_controller import router as product_router
from app.domains.discord.controllers.user_controller import router as user_router

discord_router = APIRouter()

discord_router.include_router(bot_router, prefix="/bot", tags=["Discord Bot"])
discord_router.include_router(config_router, prefix="/config", tags=["Discord Config"])
discord_router.include_router(bot_base_router, prefix="/base-bot", tags=["Discord Bot Base"])
discord_router.include_router(analytics_router, prefix="/analytics", tags=["Discord Analytics"])
discord_router.include_router(product_router, prefix="/product", tags=["Discord Product"])
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

from .bot_controller import bot_controller
from .user_controller import user_controller
from .product_controller import product_controller
from .analytics_controller import analytics_controller
from .discord_config_controller import discord_config_controller

__all__ = [
    "bot_controller",
    "user_controller",
    "product_controller",
    "analytics_controller",
    "discord_config_controller"
]
