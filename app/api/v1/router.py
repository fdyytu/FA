from fastapi import APIRouter
from app.api.v1.endpoints import health, cache

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])

# Include Discord router
try:
    from app.domains.discord.controllers.discord_controller import router as discord_router
    api_router.include_router(discord_router, prefix="/discord", tags=["discord"])
except ImportError:
    pass

# Include Discord bot management endpoints
try:
    from app.api.v1.endpoints.discord_bot import router as discord_bot_router
    api_router.include_router(discord_bot_router, prefix="/bot", tags=["discord-bot"])
except ImportError:
    pass

# Include Discord configuration endpoints
try:
    from app.api.v1.endpoints.discord_config import router as discord_config_router
    api_router.include_router(discord_config_router, prefix="/discord", tags=["discord-config"])
except ImportError:
    pass

# Include Admin endpoints
try:
    from app.domains.admin.controllers.admin_controller import router as admin_router
    api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
except ImportError:
    pass

# Include Analytics endpoints
try:
    from app.domains.analytics.controllers.analytics_controller import router as analytics_router
    api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
except ImportError:
    pass

# Include Admin Analytics endpoints
try:
    from app.domains.analytics.controllers.analytics_controller import admin_analytics_router
    api_router.include_router(admin_analytics_router, prefix="/admin/analytics", tags=["admin-analytics"])
except ImportError:
    pass

# Include Transaction endpoints
try:
    from app.domains.transaction.controllers.transaction_controller import router as transaction_router
    api_router.include_router(transaction_router, prefix="/admin/transactions", tags=["admin-transactions"])
except ImportError:
    pass
