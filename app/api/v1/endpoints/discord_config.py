"""
Discord Configuration API Endpoints
API untuk mengelola konfigurasi Discord Bot dari dashboard
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from app.core.database import get_db
from app.domains.discord.services.discord_config_service import discord_config_service
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse,
    DiscordConfigTest, DiscordConfigTestResult
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/config", response_model=Dict[str, Any])
async def create_discord_config(
    config_data: DiscordConfigCreate,
    db: Session = Depends(get_db)
):
    """Buat konfigurasi Discord baru"""
    try:
        # Create new config
        db_config = discord_config_service.create_config(db, config_data)
        
        return {
            "success": True,
            "message": "Konfigurasi Discord berhasil dibuat",
            "data": DiscordConfigResponse.from_orm(db_config)
        }
        
    except Exception as e:
        logger.error(f"Error creating Discord config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membuat konfigurasi: {str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any])
async def get_discord_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Ambil semua konfigurasi Discord"""
    try:
        configs = discord_config_service.get_all_configs(db, skip=skip, limit=limit)
        total = len(configs)
        
        return {
            "success": True,
            "data": {
                "configs": [DiscordConfigResponse.from_orm(config) for config in configs],
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting Discord configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi: {str(e)}"
        )


@router.get("/config/active", response_model=Dict[str, Any])
async def get_active_discord_config(db: Session = Depends(get_db)):
    """Ambil konfigurasi Discord yang aktif"""
    try:
        config = discord_config_service.get_active_config(db)
        
        if not config:
            return {
                "success": True,
                "message": "Tidak ada konfigurasi aktif",
                "data": None
            }
        
        return {
            "success": True,
            "data": DiscordConfigResponse.from_orm(config)
        }
        
    except Exception as e:
        logger.error(f"Error getting active Discord config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi aktif: {str(e)}"
        )


@router.get("/config/{config_id}", response_model=Dict[str, Any])
async def get_discord_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Ambil konfigurasi Discord berdasarkan ID"""
    try:
        config = discord_config_service.get_config(db, config_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        return {
            "success": True,
            "data": DiscordConfigResponse.from_orm(config)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Discord config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil konfigurasi: {str(e)}"
        )


@router.put("/config/{config_id}", response_model=Dict[str, Any])
async def update_discord_config(
    config_id: int,
    config_data: DiscordConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update konfigurasi Discord"""
    try:
        db_config = discord_config_service.update_config(db, config_id, config_data)
        
        if not db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        return {
            "success": True,
            "message": "Konfigurasi Discord berhasil diupdate",
            "data": DiscordConfigResponse.from_orm(db_config)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Discord config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengupdate konfigurasi: {str(e)}"
        )


@router.delete("/config/{config_id}", response_model=Dict[str, Any])
async def delete_discord_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Hapus konfigurasi Discord"""
    try:
        success = discord_config_service.delete_config(db, config_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        return {
            "success": True,
            "message": "Konfigurasi Discord berhasil dihapus"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Discord config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menghapus konfigurasi: {str(e)}"
        )


@router.post("/config/test", response_model=Dict[str, Any])
async def test_discord_config(config_test: DiscordConfigTest):
    """Test validitas konfigurasi Discord"""
    try:
        result = await discord_config_service.test_token(
            config_test.token,
            config_test.guild_id
        )
        
        return {
            "success": result.get('success', False),
            "message": result.get('message', 'Test completed'),
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Error testing Discord config: {e}")
        return {
            "success": False,
            "message": f"Error testing configuration: {str(e)}",
            "data": {
                "success": False,
                "errors": [str(e)]
            }
        }


@router.post("/config/{config_id}/activate", response_model=Dict[str, Any])
async def activate_discord_config(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Aktifkan konfigurasi Discord"""
    try:
        # Update config to active
        config_data = DiscordConfigUpdate(is_active=True)
        db_config = discord_config_service.update_config(db, config_id, config_data)
        
        if not db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Konfigurasi tidak ditemukan"
            )
        
        return {
            "success": True,
            "message": "Konfigurasi Discord berhasil diaktifkan",
            "data": DiscordConfigResponse.from_orm(db_config)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating Discord config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengaktifkan konfigurasi: {str(e)}"
        )
