
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.domains.discord.controllers.discord_config_controller import DiscordConfigController
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigTest
)

router = APIRouter()

@router.post("/config")
async def create_discord_config(
    config_data: DiscordConfigCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Buat konfigurasi Discord baru"""
    return await DiscordConfigController.create_config(config_data, db)

@router.get("/config")
async def get_discord_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ambil semua konfigurasi Discord"""
    return await DiscordConfigController.get_all_configs(skip, limit, db)

@router.get("/config/active")
async def get_active_discord_config(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ambil konfigurasi Discord yang aktif"""
    return await DiscordConfigController.get_active_config(db)

@router.get("/config/{config_id}")
async def get_discord_config(
    config_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ambil konfigurasi Discord berdasarkan ID"""
    return await DiscordConfigController.get_config(config_id, db)

@router.put("/config/{config_id}")
async def update_discord_config(
    config_id: int,
    config_data: DiscordConfigUpdate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update konfigurasi Discord"""
    return await DiscordConfigController.update_config(config_id, config_data, db)

@router.delete("/config/{config_id}")
async def delete_discord_config(
    config_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Hapus konfigurasi Discord"""
    return await DiscordConfigController.delete_config(config_id, db)

@router.post("/config/test")
async def test_discord_config(
    config_test: DiscordConfigTest
) -> Dict[str, Any]:
    """Test validitas konfigurasi Discord"""
    return await DiscordConfigController.test_config(config_test)

@router.post("/config/{config_id}/activate")
async def activate_discord_config(
    config_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Aktifkan konfigurasi Discord"""
    return await DiscordConfigController.activate_config(config_id, db)
