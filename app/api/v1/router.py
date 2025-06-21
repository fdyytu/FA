from fastapi import APIRouter
from app.api.v1.endpoints import health, cache
from app.common.logging.endpoint_logger import log_module_import_error
import logging

# Setup router logger
router_logger = logging.getLogger("router")

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
router_logger.info("✅ Basic endpoints registered: health, cache")

# Include Discord endpoints (API endpoints)
try:
    from app.api.v1.endpoints.discord_bot import router as discord_bot_router
    api_router.include_router(discord_bot_router, prefix="/api/discord/bot", tags=["discord-bot-api"])
    router_logger.info("✅ Discord bot API endpoints registered")
except ImportError as e:
    log_module_import_error("app.api.v1.endpoints.discord_bot", e, "Discord bot API router registration")
    router_logger.warning("⚠️ Discord bot API endpoints not available")

try:
    from app.api.v1.endpoints.discord_config import router as discord_config_router
    api_router.include_router(discord_config_router, prefix="/api/discord/config", tags=["discord-config-api"])
    router_logger.info("✅ Discord config API endpoints registered")
except ImportError as e:
    log_module_import_error("app.api.v1.endpoints.discord_config", e, "Discord config API router registration")
    router_logger.warning("⚠️ Discord config API endpoints not available")

# Include Discord domain controllers
try:
    from app.domains.discord.controllers.bot_controller import bot_controller
    api_router.include_router(bot_controller.router, prefix="/discord/bot", tags=["discord-bot"])
    router_logger.info("✅ Discord bot controller registered")
except ImportError as e:
    log_module_import_error("app.domains.discord.controllers.bot_controller", e, "Discord bot controller registration")
    router_logger.warning("⚠️ Discord bot controller not available")

try:
    from app.domains.discord.controllers.analytics_controller import analytics_controller
    api_router.include_router(analytics_controller.router, prefix="/discord/analytics", tags=["discord-analytics"])
    router_logger.info("✅ Discord analytics controller registered")
except ImportError as e:
    log_module_import_error("app.domains.discord.controllers.analytics_controller", e, "Discord analytics controller registration")
    router_logger.warning("⚠️ Discord analytics controller not available")

try:
    from app.domains.discord.controllers.user_controller import user_controller
    api_router.include_router(user_controller.router, prefix="/discord/users", tags=["discord-users"])
    router_logger.info("✅ Discord user controller registered")
except ImportError as e:
    log_module_import_error("app.domains.discord.controllers.user_controller", e, "Discord user controller registration")
    router_logger.warning("⚠️ Discord user controller not available")

try:
    from app.domains.discord.controllers.product_controller import product_controller
    api_router.include_router(product_controller.router, prefix="/discord/products", tags=["discord-products"])
    router_logger.info("✅ Discord product controller registered")
except ImportError as e:
    log_module_import_error("app.domains.discord.controllers.product_controller", e, "Discord product controller registration")
    router_logger.warning("⚠️ Discord product controller not available")

try:
    from app.domains.discord.controllers.discord_config_controller import discord_config_controller
    api_router.include_router(discord_config_controller.router, prefix="/discord/config", tags=["discord-config"])
    router_logger.info("✅ Discord config controller registered")
except ImportError as e:
    log_module_import_error("app.domains.discord.controllers.discord_config_controller", e, "Discord config controller registration")
    router_logger.warning("⚠️ Discord config controller not available")

# Include Admin endpoints
try:
    from app.domains.admin.controllers.auth_controller import auth_controller
    api_router.include_router(auth_controller.router, prefix="/admin/auth", tags=["admin-auth"])
    router_logger.info("✅ Admin auth controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.auth_controller", e, "Admin auth controller registration")
    router_logger.warning("⚠️ Admin auth controller not available")

try:
    from app.domains.admin.controllers.admin_management_controller import admin_management_controller
    api_router.include_router(admin_management_controller.router, prefix="/admin/management", tags=["admin-management"])
    router_logger.info("✅ Admin management controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.admin_management_controller", e, "Admin management controller registration")
    router_logger.warning("⚠️ Admin management controller not available")

try:
    from app.domains.admin.controllers.dashboard_controller import dashboard_controller
    api_router.include_router(dashboard_controller.router, prefix="/admin/dashboard", tags=["admin-dashboard"])
    router_logger.info("✅ Admin dashboard controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.dashboard_controller", e, "Admin dashboard controller registration")
    router_logger.warning("⚠️ Admin dashboard controller not available")

try:
    from app.domains.admin.controllers.user_management_controller import user_management_controller
    api_router.include_router(user_management_controller.router, prefix="/admin/users", tags=["admin-users"])
    router_logger.info("✅ Admin user management controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.user_management_controller", e, "Admin user management controller registration")
    router_logger.warning("⚠️ Admin user management controller not available")

try:
    from app.domains.admin.controllers.product_management_controller import product_management_controller
    api_router.include_router(product_management_controller.router, prefix="/admin/products", tags=["admin-products"])
    router_logger.info("✅ Admin product management controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.product_management_controller", e, "Admin product management controller registration")
    router_logger.warning("⚠️ Admin product management controller not available")

try:
    from app.domains.admin.controllers.configuration_controller import configuration_controller
    api_router.include_router(configuration_controller.router, prefix="/admin/config", tags=["admin-config"])
    router_logger.info("✅ Admin configuration controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.configuration_controller", e, "Admin configuration controller registration")
    router_logger.warning("⚠️ Admin configuration controller not available")

# Include Analytics endpoints
try:
    from app.domains.analytics.controllers.analytics_controller import router as analytics_router
    api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
    router_logger.info("✅ Analytics controller registered")
except ImportError as e:
    log_module_import_error("app.domains.analytics.controllers.analytics_controller", e, "Analytics controller registration")
    router_logger.warning("⚠️ Analytics controller not available")

# Include Analytics Tracking endpoints
try:
    from app.domains.analytics.controllers.analytics_tracking_controller import router as tracking_router
    api_router.include_router(tracking_router, prefix="/analytics", tags=["analytics-tracking"])
    router_logger.info("✅ Analytics tracking controller registered")
except ImportError as e:
    log_module_import_error("app.domains.analytics.controllers.analytics_tracking_controller", e, "Analytics tracking controller registration")
    router_logger.warning("⚠️ Analytics tracking controller not available")

# Include Admin Analytics endpoints
try:
    from app.domains.analytics.controllers.analytics_controller import admin_analytics_router
    api_router.include_router(admin_analytics_router, prefix="/admin/analytics", tags=["admin-analytics"])
    router_logger.info("✅ Admin analytics controller registered")
except ImportError as e:
    log_module_import_error("app.domains.analytics.controllers.analytics_controller.admin_analytics_router", e, "Admin analytics controller registration")
    router_logger.warning("⚠️ Admin analytics controller not available")

# Include Transaction endpoints - use correct path without duplication
try:
    from app.domains.admin.controllers.transaction_controller import transaction_controller
    api_router.include_router(transaction_controller.router, prefix="/admin/transactions", tags=["admin-transactions"])
    router_logger.info("✅ Admin transaction controller registered")
except ImportError as e:
    log_module_import_error("app.domains.admin.controllers.transaction_controller", e, "Admin transaction controller registration")
    router_logger.warning("⚠️ Admin transaction controller not available")

# Include User Management endpoints
try:
    from app.domains.user.controllers.user_controller import router as user_router
    api_router.include_router(user_router, prefix="/users", tags=["users"])
    router_logger.info("✅ User controller registered")
except ImportError as e:
    log_module_import_error("app.domains.user.controllers.user_controller", e, "User controller registration")
    router_logger.warning("⚠️ User controller not available")

# Include Product Management endpoints
try:
    from app.domains.product.controllers.product_controller import router as product_router
    api_router.include_router(product_router, prefix="/products", tags=["products"])
    router_logger.info("✅ Product controller registered")
except ImportError as e:
    log_module_import_error("app.domains.product.controllers.product_controller", e, "Product controller registration")
    router_logger.warning("⚠️ Product controller not available")

# Include Transaction Management endpoints
try:
    from app.domains.transaction.controllers.transaction_controller import transaction_controller as main_transaction_controller
    api_router.include_router(main_transaction_controller.router, prefix="/transactions", tags=["transactions"])
    router_logger.info("✅ Main transaction controller registered")
except ImportError as e:
    log_module_import_error("app.domains.transaction.controllers.transaction_controller", e, "Main transaction controller registration")
    router_logger.warning("⚠️ Main transaction controller not available")

# Include Wallet Management endpoints
try:
    from app.domains.wallet.controllers.wallet_controller import router as wallet_router
    api_router.include_router(wallet_router, prefix="/wallet", tags=["wallet"])
    router_logger.info("✅ Wallet controller registered")
except ImportError as e:
    log_module_import_error("app.domains.wallet.controllers.wallet_controller", e, "Wallet controller registration")
    router_logger.warning("⚠️ Wallet controller not available")

# Include Voucher Management endpoints
try:
    from app.domains.voucher.controllers.voucher_controller import router as voucher_router
    api_router.include_router(voucher_router, prefix="/vouchers", tags=["vouchers"])
    router_logger.info("✅ Voucher controller registered")
except ImportError as e:
    log_module_import_error("app.domains.voucher.controllers.voucher_controller", e, "Voucher controller registration")
    router_logger.warning("⚠️ Voucher controller not available")

# Include PPOB Management endpoints
try:
    from app.domains.ppob.controllers.ppob_controller import router as ppob_router
    api_router.include_router(ppob_router, prefix="/ppob", tags=["ppob"])
    router_logger.info("✅ PPOB controller registered")
except ImportError as e:
    log_module_import_error("app.domains.ppob.controllers.ppob_controller", e, "PPOB controller registration")
    router_logger.warning("⚠️ PPOB controller not available")

# Log router setup completion
router_logger.info("🎯 Router setup completed - All available endpoints registered")
