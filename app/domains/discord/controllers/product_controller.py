from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)

class DiscordProductController:
    """
    Controller untuk manajemen produk Discord - Single Responsibility: Discord product management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen produk Discord"""
        
        @self.router.get("/livestock", response_model=dict)
        async def get_livestock_products(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil daftar produk livestock Discord"""
            try:
                # Mock data untuk livestock products
                products = [
                    {
                        "id": f"livestock_{i}",
                        "name": f"Livestock {i}",
                        "type": "cow" if i % 2 == 0 else "chicken",
                        "price": 5000 + (i * 500),
                        "stock": 50 - i,
                        "is_available": True,
                        "description": f"High quality livestock {i}",
                        "created_at": "2025-01-16T10:00:00Z"
                    }
                    for i in range(1, min(limit + 1, 11))
                ]
                
                return {
                    "success": True,
                    "data": {
                        "products": products,
                        "total": len(products),
                        "skip": skip,
                        "limit": limit
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting livestock products: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil produk livestock: {str(e)}"
                )
        
        @self.router.get("/world-config", response_model=dict)
        async def get_world_config(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil konfigurasi world Discord"""
            try:
                # Mock data untuk world config
                config = {
                    "world_name": "GrowtopiaWorld",
                    "world_size": "100x100",
                    "max_players": 50,
                    "is_public": True,
                    "owner": "admin",
                    "settings": {
                        "allow_building": True,
                        "allow_trading": True,
                        "pvp_enabled": False,
                        "weather": "sunny"
                    },
                    "created_at": "2025-01-16T10:00:00Z",
                    "updated_at": "2025-01-16T10:00:00Z"
                }
                
                return {
                    "success": True,
                    "data": config
                }
                
            except Exception as e:
                logger.error(f"Error getting world config: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil konfigurasi world: {str(e)}"
                )

# Initialize controller
discord_product_controller = DiscordProductController()

# Export router untuk kompatibilitas dengan import
router = discord_product_controller.router

# Export controller dengan nama yang diharapkan untuk backward compatibility
product_controller = discord_product_controller
