
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from app.core.database import get_db
from app.domains.discord.services.discord_config_service import discord_config_service
from app.domains.discord.schemas.discord_config_schemas import (
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse,
    DiscordConfigTest
)

logger = logging.getLogger(__name__)

class DiscordConfigController:
    """
    Controller untuk konfigurasi Discord - Single Responsibility: Discord configuration management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk konfigurasi Discord"""
        
        @self.router.post("/", response_model=dict)
        async def create_config(
            config_data: DiscordConfigCreate,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Buat konfigurasi Discord baru"""
            try:
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
        
        @self.router.get("/", response_model=dict)
        async def get_all_configs(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil konfigurasi: {str(e)}"
            )

    @staticmethod
    async def get_active_config(db: Session) -> Dict[str, Any]:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil konfigurasi aktif: {str(e)}"
            )

    @staticmethod
    async def get_config(config_id: int, db: Session) -> Dict[str, Any]:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil konfigurasi: {str(e)}"
            )

    @staticmethod
    async def update_config(config_id: int, config_data: DiscordConfigUpdate, db: Session) -> Dict[str, Any]:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengupdate konfigurasi: {str(e)}"
            )

    @staticmethod
    async def delete_config(config_id: int, db: Session) -> Dict[str, Any]:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menghapus konfigurasi: {str(e)}"
            )

    @staticmethod
    async def test_config(config_test: DiscordConfigTest) -> Dict[str, Any]:
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
            return {
                "success": False,
                "message": f"Error testing configuration: {str(e)}",
                "data": {
                    "success": False,
                    "errors": [str(e)]
                }
            }

    @staticmethod
    async def activate_config(config_id: int, db: Session) -> Dict[str, Any]:
        try:
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengaktifkan konfigurasi: {str(e)}"
            )
