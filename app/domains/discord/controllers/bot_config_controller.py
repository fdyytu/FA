"""
Bot Configuration Controller untuk Discord Bot Management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse
)
from app.domains.discord.services.discord_config_service import DiscordConfigService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/bot-config", tags=["Bot Configuration"])

async def get_config_service():
    return DiscordConfigService()

@router.post("/", response_model=DiscordConfigResponse)
async def create_bot_config(
    config: DiscordConfigCreate,
    service: DiscordConfigService = Depends(get_config_service),
    current_user = Depends(get_current_user)
):
    """Membuat konfigurasi bot baru"""
    try:
        return await service.create_config(config, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DiscordConfigResponse])
async def get_all_configs(
    service: DiscordConfigService = Depends(get_config_service),
    current_user = Depends(get_current_user)
):
    """Mendapatkan semua konfigurasi bot"""
    return await service.get_all_configs(current_user.id)

@router.get("/{config_id}", response_model=DiscordConfigResponse)
async def get_config(
    config_id: int,
    service: DiscordConfigService = Depends(get_config_service),
    current_user = Depends(get_current_user)
):
    """Mendapatkan konfigurasi bot berdasarkan ID"""
    config = await service.get_config_by_id(config_id, current_user.id)
    if not config:
        raise HTTPException(status_code=404, detail="Konfigurasi tidak ditemukan")
    return config
