
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

@router.get("/bots")
async def get_discord_bots(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Ambil semua bot Discord"""
    try:
        # Mock data untuk bot Discord
        bots = [
            {
                "id": 1,
                "name": "PPOB Bot",
                "token": "BOT_TOKEN_1",
                "prefix": "!",
                "status": "online",
                "uptime": "99.9%",
                "commands_count": 1234,
                "last_seen": "2025-01-16T10:00:00Z",
                "guild_count": 5,
                "user_count": 150
            },
            {
                "id": 2,
                "name": "Support Bot",
                "token": "BOT_TOKEN_2", 
                "prefix": "?",
                "status": "online",
                "uptime": "98.5%",
                "commands_count": 567,
                "last_seen": "2025-01-16T09:58:00Z",
                "guild_count": 3,
                "user_count": 89
            },
            {
                "id": 3,
                "name": "Analytics Bot",
                "token": "BOT_TOKEN_3",
                "prefix": "$",
                "status": "maintenance",
                "uptime": "95.2%",
                "commands_count": 89,
                "last_seen": "2025-01-16T08:30:00Z",
                "guild_count": 1,
                "user_count": 25
            }
        ]
        
        return {
            "success": True,
            "data": bots,
            "total": len(bots)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Gagal mengambil data bot: {str(e)}"
        }
