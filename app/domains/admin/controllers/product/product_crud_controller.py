"""
Product Read Controller
Controller untuk READ operations produk
Maksimal 50 baris per file
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.domains.admin.services.product_management_service import ProductManagementService
from app.domains.admin.schemas.admin_schemas import ProductCreate, ProductUpdate, ProductResponse, PaginatedResponse
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class ProductCrudController:
    """Controller untuk CRUD operations produk - Single Responsibility"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk CRUD operations produk"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_products(
            page: int = 1, size: int = 10, search: Optional[str] = None,
            category: Optional[str] = None, is_active: Optional[bool] = None,
            current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
        ):
            """Ambil daftar produk"""
            try:
                product_service = ProductManagementService(db)
                skip = (page - 1) * size
                products, total = product_service.get_products(skip, size, search, category, is_active)
                
                logger.info(f"Retrieved {len(products)} products for admin {current_admin.username}")
                return PaginatedResponse(
                    items=[ProductResponse.from_orm(product) for product in products],
                    total=total, page=page, size=size, pages=(total + size - 1) // size
                )
            except Exception as e:
                logger.error(f"Error getting products: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get products")
        
        @self.router.get("/{product_id}", response_model=ProductResponse)
        async def get_product(
            product_id: str, current_admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
        ):
            """Ambil detail produk"""
            try:
                product_service = ProductManagementService(db)
                product = product_service.get_product_by_id(product_id)
                if not product:
                    raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
                return ProductResponse.from_orm(product)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting product {product_id}: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to get product")
