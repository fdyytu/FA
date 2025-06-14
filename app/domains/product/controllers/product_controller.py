from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.shared.responses.api_response import APIResponse
from app.domains.product.services.product_service import ProductService
from app.domains.product.repositories.product_repository import ProductRepository
from app.domains.product.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, ProductStatsResponse
)
from app.domains.product.models.product import ProductStatus
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class ProductController:
    """
    Product Controller - mengikuti SRP.
    Menangani semua endpoint terkait manajemen produk.
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/products", tags=["Products"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk produk"""
        # CRUD routes
        self.router.add_api_route(
            "/",
            self.create_product,
            methods=["POST"],
            response_model=APIResponse[ProductResponse]
        )
        self.router.add_api_route(
            "/",
            self.get_products,
            methods=["GET"],
            response_model=APIResponse[ProductListResponse]
        )
        self.router.add_api_route(
            "/{product_id}",
            self.get_product,
            methods=["GET"],
            response_model=APIResponse[ProductResponse]
        )
        self.router.add_api_route(
            "/{product_id}",
            self.update_product,
            methods=["PUT"],
            response_model=APIResponse[ProductResponse]
        )
        self.router.add_api_route(
            "/{product_id}",
            self.delete_product,
            methods=["DELETE"],
            response_model=APIResponse[dict]
        )
        
        # Search and filter routes
        self.router.add_api_route(
            "/search",
            self.search_products,
            methods=["GET"],
            response_model=APIResponse[List[ProductResponse]]
        )
        self.router.add_api_route(
            "/category/{category}",
            self.get_products_by_category,
            methods=["GET"],
            response_model=APIResponse[List[ProductResponse]]
        )
        self.router.add_api_route(
            "/code/{code}",
            self.get_product_by_code,
            methods=["GET"],
            response_model=APIResponse[ProductResponse]
        )
        
        # Management routes
        self.router.add_api_route(
            "/{product_id}/toggle-status",
            self.toggle_product_status,
            methods=["PUT"],
            response_model=APIResponse[ProductResponse]
        )
        self.router.add_api_route(
            "/stats",
            self.get_product_stats,
            methods=["GET"],
            response_model=APIResponse[ProductStatsResponse]
        )
    
    async def create_product(
        self,
        product_data: ProductCreate,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Buat produk baru (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            product = await service.create_product(product_data)
            
            return APIResponse.success_response(
                data=product,
                message="Produk berhasil dibuat"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat produk: {str(e)}"
            )
    
    async def get_products(
        self,
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        category: Optional[str] = Query(None),
        provider: Optional[str] = Query(None),
        status: Optional[ProductStatus] = Query(None)
    ) -> APIResponse[ProductListResponse]:
        """Ambil daftar produk dengan pagination"""
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            result = await service.get_products_paginated(
                page=page, size=size, category=category, provider=provider, status=status
            )
            
            return APIResponse.success_response(
                data=result,
                message="Daftar produk berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk: {str(e)}"
            )
    
    async def get_product(
        self,
        product_id: int,
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Ambil detail produk"""
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            product = repository.get_by_id(product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success_response(
                data=product,
                message="Detail produk berhasil diambil"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk: {str(e)}"
            )
    
    async def update_product(
        self,
        product_id: int,
        product_data: ProductUpdate,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Update produk (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            product = await service.update_product(product_id, product_data)
            
            return APIResponse.success_response(
                data=product,
                message="Produk berhasil diupdate"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal update produk: {str(e)}"
            )
    
    async def delete_product(
        self,
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[dict]:
        """Hapus produk (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            await service.delete_product(product_id)
            
            return APIResponse.success_response(
                data={"deleted": True},
                message="Produk berhasil dihapus"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal hapus produk: {str(e)}"
            )
    
    async def search_products(
        self,
        q: str = Query(..., description="Search term"),
        limit: int = Query(20, ge=1, le=50),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[ProductResponse]]:
        """Cari produk"""
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            products = await service.search_products(q, limit)
            
            return APIResponse.success_response(
                data=products,
                message="Pencarian produk berhasil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mencari produk: {str(e)}"
            )
    
    async def get_products_by_category(
        self,
        category: str,
        active_only: bool = Query(True),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[ProductResponse]]:
        """Ambil produk berdasarkan kategori"""
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            products = await service.get_products_by_category(category, active_only)
            
            return APIResponse.success_response(
                data=products,
                message=f"Produk kategori {category} berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk: {str(e)}"
            )
    
    async def get_product_by_code(
        self,
        code: str,
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Ambil produk berdasarkan kode"""
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            product = await service.get_product_by_code(code)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success_response(
                data=product,
                message="Produk berhasil diambil"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil produk: {str(e)}"
            )
    
    async def toggle_product_status(
        self,
        product_id: int,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Toggle status produk (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            product = await service.toggle_product_status(product_id)
            
            return APIResponse.success_response(
                data=product,
                message="Status produk berhasil diubah"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengubah status: {str(e)}"
            )
    
    async def get_product_stats(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductStatsResponse]:
        """Ambil statistik produk (Admin only)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akses admin diperlukan"
            )
        
        try:
            repository = ProductRepository(db)
            service = ProductService(repository)
            
            stats = await service.get_product_stats()
            
            return APIResponse.success_response(
                data=stats,
                message="Statistik produk berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal mengambil statistik: {str(e)}"
            )

# Instance controller
product_controller = ProductController()
router = product_controller.router
