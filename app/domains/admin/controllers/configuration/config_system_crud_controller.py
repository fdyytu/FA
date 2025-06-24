"""
Config System CRUD Controller
Controller untuk CRUD operations konfigurasi sistem
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.configuration_service import ConfigurationService
from app.domains.admin.schemas.admin_schemas import ConfigCreate, ConfigUpdate, ConfigResponse
from app.common.dependencies.admin_auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class ConfigSystemCrudController:
    """Controller untuk CRUD konfigurasi sistem - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk CRUD konfigurasi sistem"""
        
        @self.router.post("/system", response_model=ConfigResponse)
        async def create_config(
            config_data: ConfigCreate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi baru"""
            try:
                config_service = ConfigurationService(db)
                config = config_service.create_config(config_data, current_admin.id)
                logger.info(f"Config created by admin {current_admin.username}: {config_data.key}")
                return ConfigResponse.from_orm(config)
            except Exception as e:
                logger.error(f"Error creating config: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to create config")
        
        @self.router.put("/system/{key}", response_model=ConfigResponse)
        async def update_config(
            key: str, config_data: ConfigUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update konfigurasi"""
            try:
                config_service = ConfigurationService(db)
                config = config_service.update_config(key, config_data, current_admin.id)
                return ConfigResponse.from_orm(config)
            except Exception as e:
                logger.error(f"Error updating config {key}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to update config")
