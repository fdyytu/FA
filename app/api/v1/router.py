from fastapi import APIRouter
from app.api.v1.endpoints import health, cache

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])

# Include Discord endpoints (API endpoints)
try:
    from app.api.v1.endpoints.discord_bot import router as discord_bot_router
    api_router.include_router(discord_bot_router, prefix="/api/discord/bot", tags=["discord-bot-api"])
except ImportError:
    pass

try:
    from app.api.v1.endpoints.discord_config import router as discord_config_router
    api_router.include_router(discord_config_router, prefix="/api/discord/config", tags=["discord-config-api"])
except ImportError:
    pass

# Include Discord domain controllers
try:
    from app.domains.discord.controllers.bot_controller import bot_controller
    api_router.include_router(bot_controller.router, prefix="/discord/bot", tags=["discord-bot"])
except ImportError:
    pass

try:
    from app.domains.discord.controllers.analytics_controller import analytics_controller
    api_router.include_router(analytics_controller.router, prefix="/discord/analytics", tags=["discord-analytics"])
except ImportError:
    pass

try:
    from app.domains.discord.controllers.user_controller import user_controller
    api_router.include_router(user_controller.router, prefix="/discord/users", tags=["discord-users"])
except ImportError:
    pass

try:
    from app.domains.discord.controllers.product_controller import product_controller
    api_router.include_router(product_controller.router, prefix="/discord/products", tags=["discord-products"])
except ImportError:
    pass

try:
    from app.domains.discord.controllers.discord_config_controller import discord_config_controller
    api_router.include_router(discord_config_controller.router, prefix="/discord/config", tags=["discord-config"])
except ImportError:
    pass

# Include Admin endpoints
try:
    from app.domains.admin.controllers.auth_controller import auth_controller
    api_router.include_router(auth_controller.router, prefix="/admin/auth", tags=["admin-auth"])
except ImportError:
    pass

try:
    from app.domains.admin.controllers.admin_management_controller import admin_management_controller
    api_router.include_router(admin_management_controller.router, prefix="/admin/management", tags=["admin-management"])
except ImportError:
    pass

try:
    from app.domains.admin.controllers.dashboard_controller import dashboard_controller
    api_router.include_router(dashboard_controller.router, prefix="/admin/dashboard", tags=["admin-dashboard"])
except ImportError:
    pass

try:
    from app.domains.admin.controllers.user_management_controller import user_management_controller
    api_router.include_router(user_management_controller.router, prefix="/admin/users", tags=["admin-users"])
except ImportError:
    pass

try:
    from app.domains.admin.controllers.product_management_controller import product_management_controller
    api_router.include_router(product_management_controller.router, prefix="/admin/products", tags=["admin-products"])
except ImportError:
    pass

try:
    from app.domains.admin.controllers.configuration_controller import configuration_controller
    api_router.include_router(configuration_controller.router, prefix="/admin/config", tags=["admin-config"])
except ImportError:
    pass

# Include Analytics endpoints
try:
    from app.domains.analytics.controllers.analytics_controller import router as analytics_router
    api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
except ImportError:
    pass

# Include Analytics Tracking endpoints
try:
    from app.domains.analytics.controllers.analytics_tracking_controller import router as tracking_router
    api_router.include_router(tracking_router, prefix="/analytics", tags=["analytics-tracking"])
except ImportError:
    pass

# Include Admin Analytics endpoints
try:
    from app.domains.analytics.controllers.analytics_controller import admin_analytics_router
    api_router.include_router(admin_analytics_router, prefix="/admin/analytics", tags=["admin-analytics"])
except ImportError:
    pass

# Include Transaction endpoints - use correct path without duplication
try:
    from app.domains.admin.controllers.transaction_controller import transaction_controller
    api_router.include_router(transaction_controller.router, prefix="/admin/transactions", tags=["admin-transactions"])
except ImportError:
    pass

# Include User Management endpoints
try:
    from app.domains.user.controllers.user_controller import router as user_router
    api_router.include_router(user_router, prefix="/users", tags=["users"])
except ImportError:
    pass

# Include Product Management endpoints
try:
    from app.domains.product.controllers.product_controller import router as product_router
    api_router.include_router(product_router, prefix="/products", tags=["products"])
except ImportError:
    pass

# Include Transaction Management endpoints
try:
    from app.domains.transaction.controllers.transaction_controller import transaction_controller as main_transaction_controller
    api_router.include_router(main_transaction_controller.router, prefix="/transactions", tags=["transactions"])
except ImportError:
    pass

# Include Wallet Management endpoints
try:
    from app.domains.wallet.controllers.wallet_controller import router as wallet_router
    api_router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
except ImportError:
    pass

# Include Voucher Management endpoints
try:
    from app.domains.voucher.controllers.voucher_controller import router as voucher_router
    api_router.include_router(voucher_router, prefix="/vouchers", tags=["vouchers"])
except ImportError:
    pass

# Include PPOB Management endpoints
try:
    from app.domains.ppob.controllers.ppob_controller import router as ppob_router
    api_router.include_router(ppob_router, prefix="/ppob", tags=["ppob"])
except ImportError:
    pass
