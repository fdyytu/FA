from fastapi import APIRouter
from app.api.v1.endpoints import file_monitor, auth, ppob, wallet, admin, user_profile, transaction, notification

api_router = APIRouter()
api_router.include_router(file_monitor.router, prefix="/file-monitor", tags=["file-monitor"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(ppob.router, prefix="/ppob", tags=["ppob"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(user_profile.router, prefix="/users", tags=["user-profile"])
api_router.include_router(transaction.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
