from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db

# Try to import Discord models
try:
    from app.models.discord import LiveStock
except ImportError:
    LiveStock = None

# Try to import Discord schemas
try:
    from app.schemas.discord import (
        LiveStockCreate, LiveStockUpdate, LiveStockResponse
    )
except ImportError:
    LiveStockCreate = LiveStockUpdate = LiveStockResponse = None

# Try to import utility functions
try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

logger = logging.getLogger(__name__)

class LiveStockController:
    """Controller untuk manajemen LiveStock Discord"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk LiveStock management"""
        
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
            livestock_id: int,
            db: Session = Depends(get_db)
        ):
            """Ambil LiveStock berdasarkan ID"""
            try:
                if not LiveStock:
                    return create_error_response("LiveStock model not available", 503)

                livestock = db.query(LiveStock).filter(LiveStock.id == livestock_id).first()
                if not livestock:
                    raise HTTPException(status_code=404, detail="LiveStock tidak ditemukan")
                
                return create_success_response(
                    data=LiveStockResponse.from_orm(livestock) if LiveStockResponse else livestock
                )
                
            except Exception as e:
                logger.error(f"Error getting livestock: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.put("/livestocks/{livestock_id}", response_model=dict)
        async def update_livestock(
            livestock_id: int,
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
                
                update_data = livestock_data.dict(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(livestock, field, value)
                
                db.commit()
                db.refresh(livestock)
                
                return create_success_response(
                    data=LiveStockResponse.from_orm(livestock) if LiveStockResponse else livestock,
                    message="LiveStock berhasil diupdate"
                )
                
            except Exception as e:
                logger.error(f"Error updating livestock: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.delete("/livestocks/{livestock_id}", response_model=dict)
        async def delete_livestock(
            livestock_id: int,
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
                
                return create_success_response(
                    data=None,
                    message="LiveStock berhasil dihapus"
                )
                
            except Exception as e:
                logger.error(f"Error deleting livestock: {e}")
                raise HTTPException(status_code=500, detail=str(e))
