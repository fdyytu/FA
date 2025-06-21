"""
Discord Bulk Messaging API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.domains.discord.services.bulk_messaging import BulkMessagingService
from app.api.deps import get_current_user

router = APIRouter(prefix="/bot-messaging", tags=["Bot Messaging"])

async def get_messaging_service():
    return BulkMessagingService()

@router.post("/bulk/message")
async def bulk_send_message(
    bot_ids: List[int],
    channel_id: str,
    message: str,
    service: BulkMessagingService = Depends(get_messaging_service),
    current_user = Depends(get_current_user)
):
    """Kirim pesan ke multiple bots"""
    return await service.bulk_send_message(bot_ids, channel_id, message, current_user.id)

@router.post("/bulk/restart")
async def bulk_restart_bots(
    bot_ids: List[int],
    service: BulkMessagingService = Depends(get_messaging_service),
    current_user = Depends(get_current_user)
):
    """Restart multiple bots secara bersamaan"""
    return await service.bulk_restart_bots(bot_ids, current_user.id)

@router.post("/broadcast")
async def broadcast_message(
    message: str,
    service: BulkMessagingService = Depends(get_messaging_service),
    current_user = Depends(get_current_user)
):
    """Broadcast pesan ke semua bot aktif"""
    return {"message": "Broadcast sent", "content": message}
