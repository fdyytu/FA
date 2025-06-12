from fastapi import APIRouter
from app.api.v1.endpoints import file_monitor, auth, ppob, wallet

api_router = APIRouter()
api_router.include_router(file_monitor.router, prefix="/file-monitor", tags=["file-monitor"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(ppob.router, prefix="/ppob", tags=["ppob"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
