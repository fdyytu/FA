"""
Product Stats Controller
Controller untuk statistik dan kategori produk
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.product_management_service import ProductManagementService
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class ProductStatsController:
    """Controller untuk statistik produk - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk statistik produk"""
        
        @self.router.get("/categories")
        async def get_product_categories(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua kategori produk"""
            try:
                product_service = ProductManagementService(db)
                categories = product_service.get_product_categories()
                logger.info(f"Retrieved {len(categories)} product categories for admin {current_admin.username}")
                return APIResponse.success(data=categories)
            except Exception as e:
                logger.error(f"Error getting product categories: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get product categories")
        
        @self.router.get("/stats")
        async def get_product_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik produk"""
            try:
                product_service = ProductManagementService(db)
                stats = product_service.get_product_stats()
                logger.info(f"Product stats retrieved for admin {current_admin.username}")
                return APIResponse.success(data=stats)
            except Exception as e:
                logger.error(f"Error getting product stats: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get product stats")
