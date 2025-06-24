"""
Config Discord Controller
Controller untuk konfigurasi Discord
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.domains.admin.services.configuration_service import ConfigurationService
from app.domains.admin.schemas.admin_schemas import DiscordConfigCreate, DiscordConfigUpdate, DiscordConfigResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class ConfigDiscordController:
    """Controller untuk konfigurasi Discord - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk konfigurasi Discord"""
        
        @self.router.get("/discord", response_model=List[DiscordConfigResponse])
        async def get_discord_configs(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua konfigurasi Discord"""
            try:
                config_service = ConfigurationService(db)
                configs = config_service.get_discord_configs()
                logger.info(f"Retrieved {len(configs)} Discord configs for admin {current_admin.username}")
                return [DiscordConfigResponse.from_orm(config) for config in configs]
            except Exception as e:
                logger.error(f"Error getting Discord configs: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get Discord configs")
        
        @self.router.post("/discord", response_model=DiscordConfigResponse)
        async def create_discord_config(
            config_data: DiscordConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi Discord baru"""
            try:
                config_service = ConfigurationService(db)
                config = config_service.create_discord_config(config_data, current_admin.id)
                logger.info(f"Discord config created by admin {current_admin.username}")
                return DiscordConfigResponse.from_orm(config)
            except Exception as e:
                logger.error(f"Error creating Discord config: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to create Discord config")
