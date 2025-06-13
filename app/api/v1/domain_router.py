from fastapi import APIRouter
from app.domains.ppob.controllers.ppob_controller import router as ppob_router
from app.domains.wallet.controllers.wallet_controller import router as wallet_router

# Legacy endpoints (akan dihapus secara bertahap)
from app.api.v1.endpoints import file_monitor, auth, admin, user_profile, transaction, notification, product_admin, discord_admin

api_router = APIRouter()

# Domain-based routes (New Architecture)
api_router.include_router(ppob_router, prefix="/ppob", tags=["PPOB"])
api_router.include_router(wallet_router, prefix="/wallet", tags=["Wallet"])

# Legacy routes (akan dihapus secara bertahap)
api_router.include_router(file_monitor.router, prefix="/file-monitor", tags=["file-monitor"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(product_admin.router, prefix="/product-admin", tags=["product-admin"])
api_router.include_router(user_profile.router, prefix="/users", tags=["user-profile"])
api_router.include_router(transaction.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(discord_admin.router, prefix="/discord", tags=["discord-admin"])
