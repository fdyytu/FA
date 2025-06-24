"""
Product Management Controller
Controller untuk manajemen status produk (activate, deactivate, stock)
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


class ProductManagementController:
    """Controller untuk manajemen status produk - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen status produk"""
        
        @self.router.post("/{product_id}/activate")
        async def activate_product(
            product_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Aktifkan produk"""
            try:
                product_service = ProductManagementService(db)
                success = product_service.activate_product(product_id, current_admin.id)
                if not success:
                    raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
                logger.info(f"Product {product_id} activated by admin {current_admin.username}")
                return APIResponse.success(message="Produk berhasil diaktifkan")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error activating product {product_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to activate product")
        
        @self.router.post("/{product_id}/deactivate")
        async def deactivate_product(
            product_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Nonaktifkan produk"""
            try:
                product_service = ProductManagementService(db)
                success = product_service.deactivate_product(product_id, current_admin.id)
                if not success:
                    raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
                return APIResponse.success(message="Produk berhasil dinonaktifkan")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deactivating product {product_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to deactivate product")
