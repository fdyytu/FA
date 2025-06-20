from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.domains.admin.services.product_management_service import ProductManagementService
from app.domains.admin.schemas.admin_schemas import (
    ProductCreate, ProductUpdate, ProductResponse, PaginatedResponse
)
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class ProductManagementController:
    """
    Controller untuk manajemen produk - Single Responsibility: Product management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen produk"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_products(
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None,
            category: Optional[str] = None,
            is_active: Optional[bool] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar produk"""
            product_service = ProductManagementService(db)
            skip = (page - 1) * size
            
            products, total = product_service.get_products(
                skip, size, search, category, is_active
            )
            
            return PaginatedResponse(
                items=[ProductResponse.from_orm(product) for product in products],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.get("/categories")
        async def get_product_categories(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil semua kategori produk"""
            product_service = ProductManagementService(db)
            
            categories = product_service.get_product_categories()
            
            return APIResponse.success(data=categories)
        
        @self.router.get("/stats")
        async def get_product_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik produk"""
            product_service = ProductManagementService(db)
            
            stats = product_service.get_product_stats()
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/{product_id}", response_model=ProductResponse)
        async def get_product(
            product_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil detail produk"""
            product_service = ProductManagementService(db)
            
            product = product_service.get_product_by_id(product_id)
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return ProductResponse.from_orm(product)
        
        @self.router.post("/", response_model=ProductResponse)
        async def create_product(
            product_data: ProductCreate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Buat produk baru"""
            product_service = ProductManagementService(db)
            
            product = product_service.create_product(product_data, current_admin.id)
            
            return ProductResponse.from_orm(product)
        
        @self.router.put("/{product_id}", response_model=ProductResponse)
        async def update_product(
            product_id: str,
            product_data: ProductUpdate,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update produk"""
            product_service = ProductManagementService(db)
            
            product = product_service.update_product(product_id, product_data, current_admin.id)
            
            return ProductResponse.from_orm(product)
        
        @self.router.delete("/{product_id}")
        async def delete_product(
            product_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus produk"""
            product_service = ProductManagementService(db)
            
            success = product_service.delete_product(product_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(message="Produk berhasil dihapus")
        
        @self.router.post("/{product_id}/activate")
        async def activate_product(
            product_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Aktifkan produk"""
            product_service = ProductManagementService(db)
            
            success = product_service.activate_product(product_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(message="Produk berhasil diaktifkan")
        
        @self.router.post("/{product_id}/deactivate")
        async def deactivate_product(
            product_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Nonaktifkan produk"""
            product_service = ProductManagementService(db)
            
            success = product_service.deactivate_product(product_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(message="Produk berhasil dinonaktifkan")
        
        @self.router.post("/{product_id}/update-stock")
        async def update_product_stock(
            product_id: str,
            stock: int,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update stok produk"""
            product_service = ProductManagementService(db)
            
            success = product_service.update_product_stock(product_id, stock, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(message="Stok produk berhasil diupdate")


# Initialize controller
product_management_controller = ProductManagementController()
