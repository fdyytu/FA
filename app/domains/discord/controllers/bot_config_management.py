"""
Bot Configuration Management - Update & Delete Operations
"""
from fastapi import APIRouter, HTTPException, Depends
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigUpdate, DiscordConfigResponse
)
from app.domains.discord.services.discord_config_service import DiscordConfigService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/bot-config", tags=["Bot Configuration Management"])

async def get_config_service():
    return DiscordConfigService()

@router.put("/{config_id}", response_model=DiscordConfigResponse)
async def update_config(
    config_id: int,
    config_update: DiscordConfigUpdate,
    service: DiscordConfigService = Depends(get_config_service),
    current_user = Depends(get_current_user)
):
    """Update konfigurasi bot"""
    try:
        return await service.update_config(config_id, config_update, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{config_id}")
async def delete_config(
    config_id: int,
    service: DiscordConfigService = Depends(get_config_service),
    current_user = Depends(get_current_user)
):
    """Hapus konfigurasi bot"""
    success = await service.delete_config(config_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Konfigurasi tidak ditemukan")
    return {"message": "Konfigurasi berhasil dihapus"}

@router.post("/{config_id}/validate")
async def validate_config(
    config_id: int,
    service: DiscordConfigService = Depends(get_config_service),
    current_user = Depends(get_current_user)
):
    """Validasi konfigurasi bot"""
    result = await service.validate_config(config_id, current_user.id)
    return {"valid": result, "message": "Valid" if result else "Invalid"}
