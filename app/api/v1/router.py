from fastapi import APIRouter
from app.api.v1.endpoints import health, cache

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
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
