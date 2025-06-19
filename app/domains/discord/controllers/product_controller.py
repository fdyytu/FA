from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import LiveStock, AdminWorldConfig
except ImportError:
    LiveStock = AdminWorldConfig = None

# Try to import Discord schemas
try:
    from app.schemas.discord import (
        LiveStockCreate, LiveStockUpdate, LiveStockResponse,
        AdminWorldConfigCreate, AdminWorldConfigUpdate, AdminWorldConfigResponse
    )
except ImportError:
    LiveStockCreate = LiveStockUpdate = LiveStockResponse = None
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


class DiscordProductController:
    """
    Controller untuk manajemen produk Discord - Single Responsibility: Discord product and world management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen produk Discord"""
        
        # LiveStock Management Routes
        @self.router.get("/livestocks", response_model=dict)
        async def get_livestocks(
            skip: int = 0,
            limit: int = 100,
            is_active: Optional[bool] = None,
            db: Session = Depends(get_db)
        ):
            """Ambil daftar LiveStock"""
            try:
                if not LiveStock:
                    return create_success_response(
                        data={
                            "livestocks": [],
                            "total": 0,
                            "skip": skip,
                            "limit": limit
                        }
                    )

                query = db.query(LiveStock)
                if is_active is not None:
                    query = query.filter(LiveStock.is_active == is_active)
                
                livestocks = query.offset(skip).limit(limit).all()
                total = query.count()
                
                # Manual conversion since schema might not be available
                livestock_list = []
                for livestock in livestocks:
                    livestock_dict = {
                        "id": livestock.id,
                        "name": livestock.name,
                        "description": livestock.description,
                        "price": float(livestock.price) if livestock.price else 0,
                        "stock": livestock.stock,
                        "is_active": livestock.is_active,
                        "created_at": livestock.created_at.isoformat() if livestock.created_at else None,
                        "updated_at": livestock.updated_at.isoformat() if livestock.updated_at else None
                    }
                    livestock_list.append(livestock_dict)
                
                return create_success_response(
                    data={
                        "livestocks": livestock_list,
                        "total": total,
                        "skip": skip,
                        "limit": limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting livestocks: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/livestocks", response_model=dict)
        async def create_livestock(
            livestock_data: LiveStockCreate,
            db: Session = Depends(get_db)
        ):
            """Buat LiveStock baru"""
            try:
                if not LiveStock:
                    return create_error_response("LiveStock model not available", 503)

                new_livestock = LiveStock(**livestock_data.dict())
                db.add(new_livestock)
                db.commit()
                db.refresh(new_livestock)
                
                return create_success_response(
                    data=LiveStockResponse.from_orm(new_livestock) if LiveStockResponse else new_livestock,
                    message="LiveStock berhasil dibuat"
                )
                
            except Exception as e:
                logger.error(f"Error creating livestock: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/livestocks/{livestock_id}", response_model=dict)
        async def get_livestock(
            livestock_id: str,
            db: Session = Depends(get_db)
        ):
            """Ambil detail LiveStock"""
            try:
                if not LiveStock:
                    return create_error_response("LiveStock model not available", 503)

                livestock = db.query(LiveStock).filter(LiveStock.id == livestock_id).first()
                
                if not livestock:
                    raise HTTPException(status_code=404, detail="LiveStock tidak ditemukan")
                
                livestock_dict = {
                    "id": livestock.id,
                    "name": livestock.name,
                    "description": livestock.description,
                    "price": float(livestock.price) if livestock.price else 0,
                    "stock": livestock.stock,
                    "is_active": livestock.is_active,
                    "created_at": livestock.created_at.isoformat() if livestock.created_at else None,
                    "updated_at": livestock.updated_at.isoformat() if livestock.updated_at else None
                }
                
                return create_success_response(data=livestock_dict)
                
            except Exception as e:
                logger.error(f"Error getting livestock {livestock_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/livestocks/{livestock_id}", response_model=dict)
        async def update_livestock(
            livestock_id: str,
            livestock_data: LiveStockUpdate,
            db: Session = Depends(get_db)
        ):
            """Update LiveStock"""
            try:
                if not LiveStock:
                    return create_error_response("LiveStock model not available", 503)

                livestock = db.query(LiveStock).filter(LiveStock.id == livestock_id).first()
                
                if not livestock:
                    raise HTTPException(status_code=404, detail="LiveStock tidak ditemukan")
                
                # Update livestock data
                for field, value in livestock_data.dict(exclude_unset=True).items():
                    setattr(livestock, field, value)
                
                db.commit()
                db.refresh(livestock)
                
                return create_success_response(
                    data=LiveStockResponse.from_orm(livestock) if LiveStockResponse else livestock,
                    message="LiveStock berhasil diupdate"
                )
                
            except Exception as e:
                logger.error(f"Error updating livestock {livestock_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/livestocks/{livestock_id}")
        async def delete_livestock(
            livestock_id: str,
            db: Session = Depends(get_db)
        ):
            """Hapus LiveStock"""
            try:
                if not LiveStock:
                    return create_error_response("LiveStock model not available", 503)

                livestock = db.query(LiveStock).filter(LiveStock.id == livestock_id).first()
                
                if not livestock:
                    raise HTTPException(status_code=404, detail="LiveStock tidak ditemukan")
                
                db.delete(livestock)
                db.commit()
                
                return create_success_response(message="LiveStock berhasil dihapus")
                
            except Exception as e:
                logger.error(f"Error deleting livestock {livestock_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # World Configuration Routes
        @self.router.get("/worlds", response_model=dict)
        async def get_world_configs(
            skip: int = 0,
            limit: int = 100,
            is_active: Optional[bool] = None,
            db: Session = Depends(get_db)
        ):
            """Ambil daftar World Configuration"""
            try:
                if not AdminWorldConfig:
                    return create_success_response(
                        data={
                            "worlds": [],
                            "total": 0,
                            "skip": skip,
                            "limit": limit
                        }
                    )

                query = db.query(AdminWorldConfig)
                if is_active is not None:
                    query = query.filter(AdminWorldConfig.is_active == is_active)
                
                worlds = query.offset(skip).limit(limit).all()
                total = query.count()
                
                # Manual conversion since schema might not be available
                world_list = []
                for world in worlds:
                    world_dict = {
                        "id": world.id,
                        "world_name": world.world_name,
                        "description": world.description,
                        "is_active": world.is_active,
                        "created_at": world.created_at.isoformat() if world.created_at else None,
                        "updated_at": world.updated_at.isoformat() if world.updated_at else None
                    }
                    world_list.append(world_dict)
                
                return create_success_response(
                    data={
                        "worlds": world_list,
                        "total": total,
                        "skip": skip,
                        "limit": limit
                    }
                )
                
            except Exception as e:
                logger.error(f"Error getting world configs: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/worlds", response_model=dict)
        async def create_world_config(
            world_data: AdminWorldConfigCreate,
            db: Session = Depends(get_db)
        ):
            """Buat World Configuration baru"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                new_world = AdminWorldConfig(**world_data.dict())
                db.add(new_world)
                db.commit()
                db.refresh(new_world)
                
                return create_success_response(
                    data=AdminWorldConfigResponse.from_orm(new_world) if AdminWorldConfigResponse else new_world,
                    message="World Configuration berhasil dibuat"
                )
                
            except Exception as e:
                logger.error(f"Error creating world config: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/worlds/{world_id}", response_model=dict)
        async def get_world_config(
            world_id: str,
            db: Session = Depends(get_db)
        ):
            """Ambil detail World Configuration"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                world = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == world_id).first()
                
                if not world:
                    raise HTTPException(status_code=404, detail="World Configuration tidak ditemukan")
                
                world_dict = {
                    "id": world.id,
                    "world_name": world.world_name,
                    "description": world.description,
                    "is_active": world.is_active,
                    "created_at": world.created_at.isoformat() if world.created_at else None,
                    "updated_at": world.updated_at.isoformat() if world.updated_at else None
                }
                
                return create_success_response(data=world_dict)
                
            except Exception as e:
                logger.error(f"Error getting world config {world_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/worlds/{world_id}", response_model=dict)
        async def update_world_config(
            world_id: str,
            world_data: AdminWorldConfigUpdate,
            db: Session = Depends(get_db)
        ):
            """Update World Configuration"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                world = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == world_id).first()
                
                if not world:
                    raise HTTPException(status_code=404, detail="World Configuration tidak ditemukan")
                
                # Update world data
                for field, value in world_data.dict(exclude_unset=True).items():
                    setattr(world, field, value)
                
                db.commit()
                db.refresh(world)
                
                return create_success_response(
                    data=AdminWorldConfigResponse.from_orm(world) if AdminWorldConfigResponse else world,
                    message="World Configuration berhasil diupdate"
                )
                
            except Exception as e:
                logger.error(f"Error updating world config {world_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/worlds/{world_id}")
        async def delete_world_config(
            world_id: str,
            db: Session = Depends(get_db)
        ):
            """Hapus World Configuration"""
            try:
                if not AdminWorldConfig:
                    return create_error_response("AdminWorldConfig model not available", 503)

                world = db.query(AdminWorldConfig).filter(AdminWorldConfig.id == world_id).first()
                
                if not world:
                    raise HTTPException(status_code=404, detail="World Configuration tidak ditemukan")
                
                db.delete(world)
                db.commit()
                
                return create_success_response(message="World Configuration berhasil dihapus")
                
            except Exception as e:
                logger.error(f"Error deleting world config {world_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))


# Initialize controller
product_controller = DiscordProductController()
