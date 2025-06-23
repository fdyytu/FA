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
                logger.error(f"Error getting Discord configs: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil konfigurasi: {str(e)}"
                )

        @self.router.get("/active", response_model=dict)
        async def get_active_config(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
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



        @self.router.get("/bots", response_model=dict)
        async def get_discord_bots(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil semua bot Discord"""
            try:
                # Mock data untuk bot Discord - sesuai dengan yang ada di API endpoint
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
                logger.error(f"Error getting Discord bots: {e}")
                return {
                    "success": False,
                    "message": f"Gagal mengambil data bot: {str(e)}"
                }

        @self.router.get("/worlds", response_model=dict)
        async def get_discord_worlds(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil semua world Discord"""
            try:
                # Mock data untuk world Discord
                worlds = [
                    {
                        "id": 1,
                        "name": "PPOB World",
                        "owner": "Admin",
                        "bot_name": "PPOB Bot",
                        "is_active": True,
                        "created_at": "2025-01-15T10:00:00Z",
                        "member_count": 150
                    },
                    {
                        "id": 2,
                        "name": "Support World",
                        "owner": "Support Team",
                        "bot_name": "Support Bot",
                        "is_active": True,
                        "created_at": "2025-01-14T15:30:00Z",
                        "member_count": 89
                    },
                    {
                        "id": 3,
                        "name": "Analytics World",
                        "owner": "Analytics Team",
                        "bot_name": "Analytics Bot",
                        "is_active": False,
                        "created_at": "2025-01-13T09:15:00Z",
                        "member_count": 25
                    }
                ]
                
                return {
                    "success": True,
                    "data": worlds,
                    "total": len(worlds)
                }
                
            except Exception as e:
                logger.error(f"Error getting Discord worlds: {e}")
                return {
                    "success": False,
                    "message": f"Gagal mengambil data world: {str(e)}"
                }

        @self.router.post("/test", response_model=dict)
        async def test_config(
            config_data: DiscordConfigTest,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Test konfigurasi Discord"""
            try:
                result = discord_config_service.test_config(config_data)
                return {
                    "success": True,
                    "message": "Test konfigurasi berhasil",
                    "data": result
                }
            except Exception as e:
                logger.error(f"Error testing Discord config: {e}")
                return {
                    "success": False,
                    "message": "Test konfigurasi gagal",
                    "error": str(e)
                }

        @self.router.get("/{config_id}", response_model=dict)
        async def get_config(
            config_id: int,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
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
                logger.error(f"Error getting Discord config {config_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil konfigurasi: {str(e)}"
                )

        @self.router.put("/{config_id}", response_model=dict)
        async def update_config(
            config_id: int,
            config_data: DiscordConfigUpdate,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Update konfigurasi Discord"""
            try:
                config = discord_config_service.update_config(db, config_id, config_data)
                if not config:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Konfigurasi tidak ditemukan"
                    )
                return {
                    "success": True,
                    "message": "Konfigurasi berhasil diupdate",
                    "data": DiscordConfigResponse.from_orm(config)
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error updating Discord config {config_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengupdate konfigurasi: {str(e)}"
                )

        @self.router.delete("/{config_id}")
        async def delete_config(
            config_id: int,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
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
                    "message": "Konfigurasi berhasil dihapus"
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting Discord config {config_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal menghapus konfigurasi: {str(e)}"
                )

        @self.router.post("/{config_id}/activate")
        async def activate_config(
            config_id: int,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Aktifkan konfigurasi Discord"""
            try:
                config = discord_config_service.activate_config(db, config_id)
                if not config:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Konfigurasi tidak ditemukan"
                    )
                return {
                    "success": True,
                    "message": "Konfigurasi berhasil diaktifkan",
                    "data": DiscordConfigResponse.from_orm(config)
                }
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error activating Discord config {config_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengaktifkan konfigurasi: {str(e)}"
                )


# Initialize controller
discord_config_controller = DiscordConfigController()

# Export router untuk kompatibilitas dengan import
router = discord_config_controller.router
