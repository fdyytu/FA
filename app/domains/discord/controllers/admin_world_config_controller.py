from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import AdminWorldConfig
except ImportError:
    AdminWorldConfig = None

# Try to import Discord schemas
try:
    from app.schemas.discord import (
        AdminWorldConfigCreate, AdminWorldConfigUpdate, AdminWorldConfigResponse
    )
except ImportError:
    AdminWorldConfigCreate = AdminWorldConfigUpdate = AdminWorldConfigResponse = None

# Try to import utility functions
try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

logger = logging.getLogger(__name__)

class AdminWorldConfigController:
    """Controller untuk manajemen AdminWorldConfig Discord"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk AdminWorldConfig management"""
        
        @self.router.get("/admin-world-configs", response_model=dict)
        async def get_admin_world_configs(
            skip: int = 0,
            limit: int = 100,
            is_active: Optional[bool] = None,
            db: Session = Depends(get_db)
        ):
            """Ambil daftar AdminWorldConfig"""
            try:
                if not AdminWorldConfig:
                    return create_success_response(
                        data={
                            "configs": [],
                            "total": 0,
                            "skip": skip,
                            "limit": limit
                        }
                    )

                query = db.query(AdminWorldConfig)
                if is_active is not None:
                    query = query.filter(AdminWorldConfig.is_active == is_active)
                
                configs = query.offset(skip).limit(limit).all()
                total = query.count()
                
                # Manual conversion since schema might not be available
                config_list = []
                for config in configs:
                    config_dict = {
                        "id": config.id,
                        "world_name": config.world_name,
                        "admin_id": config.admin_id,
                        "config_data": config.config_data,
                        "is_active": config.is_active,
                        "created_at": config.created_at.isoformat() if config.created_at else None,
                        "updated_at": config.updated_at.isoformat() if config.updated_at else None
                    }
                    config_list.append(config_dict)
                
                return create_success_response(
                    data={
                        "configs": config_list,
                        "total": total,
                        "skip": skip,
                        "limit": limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting admin world configs: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/admin-world-configs", response_model=dict)
        async def create_admin_world_config(
            config_data: AdminWorldConfigCreate,
            db: Session = Depends(get_db)
        ):
            """Buat AdminWorldConfig baru"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                new_config = AdminWorldConfig(**config_data.dict())
                db.add(new_config)
                db.commit()
                db.refresh(new_config)
                
                return create_success_response(
                    data=AdminWorldConfigResponse.from_orm(new_config) if AdminWorldConfigResponse else new_config,
                    message="AdminWorldConfig berhasil dibuat"
                )
                
            except Exception as e:
                logger.error(f"Error creating admin world config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/admin-world-configs/{config_id}", response_model=dict)
        async def get_admin_world_config(
            config_id: int,
            db: Session = Depends(get_db)
        ):
            """Ambil AdminWorldConfig berdasarkan ID"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                config = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == config_id).first()
                if not config:
                    raise HTTPException(status_code=404, detail="AdminWorldConfig tidak ditemukan")
                
                return create_success_response(
                    data=AdminWorldConfigResponse.from_orm(config) if AdminWorldConfigResponse else config
                )
                
            except Exception as e:
                logger.error(f"Error getting admin world config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/admin-world-configs/{config_id}", response_model=dict)
        async def update_admin_world_config(
            config_id: int,
            config_data: AdminWorldConfigUpdate,
            db: Session = Depends(get_db)
        ):
            """Update AdminWorldConfig"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                config = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == config_id).first()
                if not config:
                    raise HTTPException(status_code=404, detail="AdminWorldConfig tidak ditemukan")
                
                update_data = config_data.dict(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(config, field, value)
                
                db.commit()
                db.refresh(config)
                
                return create_success_response(
                    data=AdminWorldConfigResponse.from_orm(config) if AdminWorldConfigResponse else config,
                    message="AdminWorldConfig berhasil diupdate"
                )
                
            except Exception as e:
                logger.error(f"Error updating admin world config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/admin-world-configs/{config_id}", response_model=dict)
        async def delete_admin_world_config(
            config_id: int,
            db: Session = Depends(get_db)
        ):
            """Hapus AdminWorldConfig"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                config = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == config_id).first()
                if not config:
                    raise HTTPException(status_code=404, detail="AdminWorldConfig tidak ditemukan")
                
                db.delete(config)
                db.commit()
                
                return create_success_response(
                    data=None,
                    message="AdminWorldConfig berhasil dihapus"
                )
                
            except Exception as e:
                logger.error(f"Error deleting admin world config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/admin-world-configs/by-world/{world_name}", response_model=dict)
        async def get_configs_by_world(
            world_name: str,
            db: Session = Depends(get_db)
        ):
            """Ambil konfigurasi berdasarkan nama world"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                configs = db.query(AdminWorldConfig).filter(
                    AdminWorldConfig.world_name == world_name,
                    AdminWorldConfig.is_active == True
                ).all()
                
                config_list = []
                for config in configs:
                    config_dict = {
                        "id": config.id,
                        "world_name": config.world_name,
                        "admin_id": config.admin_id,
                        "config_data": config.config_data,
                        "is_active": config.is_active,
                        "created_at": config.created_at.isoformat() if config.created_at else None,
                        "updated_at": config.updated_at.isoformat() if config.updated_at else None
                    }
                    config_list.append(config_dict)
                
                return create_success_response(
                    data={"configs": config_list, "world_name": world_name}
                )
                
            except Exception as e:
                logger.error(f"Error getting configs by world: {e}")
                raise HTTPException(status_code=500, detail=str(e))
