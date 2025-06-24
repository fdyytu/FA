"""
Product Write Controller
Controller untuk CREATE/UPDATE/DELETE operations produk
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.product_management_service import ProductManagementService
from app.domains.admin.schemas.admin_schemas import ProductCreate, ProductUpdate, ProductResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class ProductWriteController:
    """Controller untuk write operations produk - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk write operations produk"""
        
        @self.router.post("/", response_model=ProductResponse)
        async def create_product(
            product_data: ProductCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat produk baru"""
            try:
                product_service = ProductManagementService(db)
                product = product_service.create_product(product_data, current_admin.id)
                logger.info(f"Product created by admin {current_admin.username}: {product.id}")
                return ProductResponse.from_orm(product)
            except Exception as e:
                logger.error(f"Error creating product: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to create product")
        
        @self.router.put("/{product_id}", response_model=ProductResponse)
        async def update_product(
            product_id: str, product_data: ProductUpdate,
            current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
        ):
            """Update produk"""
            try:
                product_service = ProductManagementService(db)
                product = product_service.update_product(product_id, product_data, current_admin.id)
                return ProductResponse.from_orm(product)
            except Exception as e:
                logger.error(f"Error updating product {product_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to update product")
