"""
Enhanced Bot Management API - Core Operations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.domains.discord.services.bulk_operations import BulkOperationsService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/bot-management", tags=["Enhanced Bot Management"])

async def get_bulk_service():
    return BulkOperationsService()

@router.post("/bulk/start")
async def bulk_start_bots(
    bot_ids: List[int],
    service: BulkOperationsService = Depends(get_bulk_service),
    current_user = Depends(get_current_user)
):
    """Start multiple bots secara bersamaan"""
    try:
        return await service.bulk_start_bots(bot_ids, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk/stop")
async def bulk_stop_bots(
    bot_ids: List[int],
    service: BulkOperationsService = Depends(get_bulk_service),
    current_user = Depends(get_current_user)
):
    """Stop multiple bots secara bersamaan"""
    try:
        return await service.bulk_stop_bots(bot_ids, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/bulk/status")
async def get_bulk_status(
    bot_ids: List[int],
    service: BulkOperationsService = Depends(get_bulk_service),
    current_user = Depends(get_current_user)
):
    """Dapatkan status multiple bots"""
    try:
        # Implementation untuk get bulk status
        return {"bot_ids": bot_ids, "status": "checked"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
