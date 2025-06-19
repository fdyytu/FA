from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.domains.admin.services.admin_service import ConfigurationService, MarginManagementService
from app.domains.admin.schemas.admin_schemas import (
    ConfigCreate, ConfigUpdate, ConfigResponse, MarginConfigCreate, 
    MarginConfigUpdate, MarginConfigResponse, PaginatedResponse,
    DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse
)
from app.shared.dependencies.admin_auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class ConfigurationController:
    """
    Controller untuk konfigurasi sistem - Single Responsibility: System configuration endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk konfigurasi sistem"""
        
        # System Configuration Routes
        @self.router.get("/system", response_model=List[ConfigResponse])
        async def get_configs(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua konfigurasi sistem"""
            config_service = ConfigurationService(db)
            
            configs = config_service.get_all_configs()
            
            return [ConfigResponse.from_orm(config) for config in configs]
        
        @self.router.get("/system/{key}", response_model=ConfigResponse)
        async def get_config(
            key: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil konfigurasi berdasarkan key"""
            config_service = ConfigurationService(db)
            
            config = config_service.get_config_by_key(key)
            
            if not config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi tidak ditemukan"
                )
            
            return ConfigResponse.from_orm(config)
        
        @self.router.post("/system", response_model=ConfigResponse)
        async def create_config(
            config_data: ConfigCreate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi baru"""
            config_service = ConfigurationService(db)
            
            config = config_service.create_config(config_data, current_admin.id)
            
            return ConfigResponse.from_orm(config)
        
        @self.router.put("/system/{key}", response_model=ConfigResponse)
        async def update_config(
            key: str,
            config_data: ConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi"""
            config_service = ConfigurationService(db)
            
            config = config_service.update_config(key, config_data, current_admin.id)
            
            return ConfigResponse.from_orm(config)
        
        @self.router.delete("/system/{key}")
        async def delete_config(
            key: str,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus konfigurasi"""
            config_service = ConfigurationService(db)
            
            success = config_service.delete_config(key, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi tidak ditemukan"
                )
            
            return {"message": "Konfigurasi berhasil dihapus"}
        
        # Margin Configuration Routes
        @self.router.get("/margins", response_model=List[MarginConfigResponse])
        async def get_margin_configs(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua konfigurasi margin"""
            margin_service = MarginManagementService(db)
            
            margins = margin_service.get_all_margins()
            
            return [MarginConfigResponse.from_orm(margin) for margin in margins]
        
        @self.router.post("/margins", response_model=MarginConfigResponse)
        async def create_margin_config(
            margin_data: MarginConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi margin baru"""
            margin_service = MarginManagementService(db)
            
            margin = margin_service.create_margin(margin_data, current_admin.id)
            
            return MarginConfigResponse.from_orm(margin)
        
        @self.router.put("/margins/{margin_id}", response_model=MarginConfigResponse)
        async def update_margin_config(
            margin_id: str,
            margin_data: MarginConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi margin"""
            margin_service = MarginManagementService(db)
            
            margin = margin_service.update_margin(margin_id, margin_data, current_admin.id)
            
            return MarginConfigResponse.from_orm(margin)
        
        @self.router.delete("/margins/{margin_id}")
        async def delete_margin_config(
            margin_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus konfigurasi margin"""
            margin_service = MarginManagementService(db)
            
            success = margin_service.delete_margin(margin_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi margin tidak ditemukan"
                )
            
            return {"message": "Konfigurasi margin berhasil dihapus"}
        
        # Discord Configuration Routes
        @self.router.get("/discord", response_model=List[DiscordConfigResponse])
        async def get_discord_configs(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua konfigurasi Discord"""
            config_service = ConfigurationService(db)
            
            configs = config_service.get_discord_configs()
            
            return [DiscordConfigResponse.from_orm(config) for config in configs]
        
        @self.router.post("/discord", response_model=DiscordConfigResponse)
        async def create_discord_config(
            config_data: DiscordConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi Discord baru"""
            config_service = ConfigurationService(db)
            
            config = config_service.create_discord_config(config_data, current_admin.id)
            
            return DiscordConfigResponse.from_orm(config)
        
        @self.router.put("/discord/{config_id}", response_model=DiscordConfigResponse)
        async def update_discord_config(
            config_id: str,
            config_data: DiscordConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi Discord"""
            config_service = ConfigurationService(db)
            
            config = config_service.update_discord_config(config_id, config_data, current_admin.id)
            
            return DiscordConfigResponse.from_orm(config)
        
        @self.router.delete("/discord/{config_id}")
        async def delete_discord_config(
            config_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus konfigurasi Discord"""
            config_service = ConfigurationService(db)
            
            success = config_service.delete_discord_config(config_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Konfigurasi Discord tidak ditemukan"
                )
            
            return {"message": "Konfigurasi Discord berhasil dihapus"}


# Initialize controller
configuration_controller = ConfigurationController()
