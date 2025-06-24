"""
Config Margin Controller
Controller untuk konfigurasi margin
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.domains.admin.services.margin_management_service import MarginManagementService
from app.domains.admin.schemas.admin_schemas import MarginConfigCreate, MarginConfigUpdate, MarginConfigResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class ConfigMarginController:
    """Controller untuk konfigurasi margin - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk konfigurasi margin"""
        
        @self.router.get("/margins", response_model=List[MarginConfigResponse])
        async def get_margin_configs(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua konfigurasi margin"""
            try:
                margin_service = MarginManagementService(db)
                margins = margin_service.get_all_margins()
                logger.info(f"Retrieved {len(margins)} margin configs for admin {current_admin.username}")
                return [MarginConfigResponse.from_orm(margin) for margin in margins]
            except Exception as e:
                logger.error(f"Error getting margin configs: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get margin configs")
        
        @self.router.post("/margins", response_model=MarginConfigResponse)
        async def create_margin_config(
            margin_data: MarginConfigCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat konfigurasi margin baru"""
            try:
                margin_service = MarginManagementService(db)
                margin = margin_service.create_margin(margin_data, current_admin.id)
                logger.info(f"Margin config created by admin {current_admin.username}")
                return MarginConfigResponse.from_orm(margin)
            except Exception as e:
                logger.error(f"Error creating margin config: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to create margin config")
