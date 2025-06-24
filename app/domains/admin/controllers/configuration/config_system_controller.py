"""
Config System Controller
Controller untuk konfigurasi sistem
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.domains.admin.services.configuration_service import ConfigurationService
from app.domains.admin.schemas.admin_schemas import ConfigCreate, ConfigUpdate, ConfigResponse
from app.common.dependencies.admin_auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class ConfigSystemController:
    """Controller untuk konfigurasi sistem - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk konfigurasi sistem"""
        
        @self.router.get("/system", response_model=List[ConfigResponse])
        async def get_configs(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua konfigurasi sistem"""
            try:
                config_service = ConfigurationService(db)
                configs = config_service.get_all_configs()
                logger.info(f"Retrieved {len(configs)} system configs for admin {current_admin.username}")
                return [ConfigResponse.from_orm(config) for config in configs]
            except Exception as e:
                logger.error(f"Error getting system configs: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get system configs")
        
        @self.router.get("/system/{key}", response_model=ConfigResponse)
        async def get_config(
            key: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil konfigurasi berdasarkan key"""
            try:
                config_service = ConfigurationService(db)
                config = config_service.get_config_by_key(key)
                if not config:
                    raise HTTPException(status_code=404, detail="Konfigurasi tidak ditemukan")
                return ConfigResponse.from_orm(config)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting config {key}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get config")
