from fastapi import APIRouter
from app.domains.auth.controllers.auth_controller import router as auth_router

# Import router dari domain lain akan ditambahkan setelah domain tersebut direstrukturisasi
# from app.domains.ppob.controllers.ppob_controller import router as ppob_router
# from app.domains.wallet.controllers.wallet_controller import router as wallet_router
# from app.domains.transaction.controllers.transaction_controller import router as transaction_router
# from app.domains.user.controllers.user_profile_controller import router as user_profile_router
# from app.domains.admin.controllers.admin_controller import router as admin_router
# from app.domains.product.controllers.product_controller import router as product_router
# from app.domains.notification.controllers.notification_controller import router as notification_router
# from app.domains.file_monitor.controllers.file_monitor_controller import router as file_monitor_router

# Import router lama untuk backward compatibility (akan dihapus setelah semua domain direstrukturisasi)
from app.api.v1.endpoints import (
    ppob, wallet, admin, user_profile, transaction, 
    notification, product_admin, file_monitor
)

api_router = APIRouter()

# Domain-based routes (new structure)
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Legacy routes (akan dipindahkan ke domain masing-masing)
api_router.include_router(file_monitor.router, prefix="/file-monitor", tags=["file-monitor"])
api_router.include_router(ppob.router, prefix="/ppob", tags=["ppob"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(product_admin.router, prefix="/product-admin", tags=["product-admin"])
api_router.include_router(user_profile.router, prefix="/users", tags=["user-profile"])
api_router.include_router(transaction.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FA Application is running"}
