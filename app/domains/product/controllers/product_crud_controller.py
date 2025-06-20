from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.common.responses.api_response import APIResponse
from app.domains.product.services.product_service import ProductService
from app.domains.product.repositories.product_repository import ProductRepository
from app.domains.product.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
)
from app.domains.product.models.product import ProductStatus
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class ProductCRUDController:
    """
    Product CRUD Controller - menangani operasi Create, Read, Update, Delete produk
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/products", tags=["Product CRUD"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk CRUD produk"""
        
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
    
    async def create_product(
        self,
        product_data: ProductCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[ProductResponse]:
        """Buat produk baru"""
        try:
            product_service = ProductService(db)
            product = await product_service.create_product(product_data)
            
            return APIResponse.success(
                data=ProductResponse.from_orm(product),
                message="Produk berhasil dibuat"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get_products(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        status_filter: Optional[ProductStatus] = None,
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductListResponse]:
        """Ambil daftar produk dengan pagination"""
        try:
            product_service = ProductService(db)
            products, total = await product_service.get_products(
                skip=skip, 
                limit=limit, 
                status_filter=status_filter
            )
            
            product_responses = [ProductResponse.from_orm(p) for p in products]
            
            return APIResponse.success(
                data=ProductListResponse(
                    products=product_responses,
                    total=total,
                    skip=skip,
                    limit=limit
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_product(
        self,
        product_id: str,
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Ambil produk berdasarkan ID"""
        try:
            product_service = ProductService(db)
            product = await product_service.get_product_by_id(product_id)
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(
                data=ProductResponse.from_orm(product)
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_product(
        self,
        product_id: str,
        product_data: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[ProductResponse]:
        """Update produk"""
        try:
            product_service = ProductService(db)
            product = await product_service.update_product(product_id, product_data)
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(
                data=ProductResponse.from_orm(product),
                message="Produk berhasil diupdate"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def delete_product(
        self,
        product_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[dict]:
        """Hapus produk (soft delete)"""
        try:
            product_service = ProductService(db)
            success = await product_service.delete_product(product_id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            return APIResponse.success(
                data={"deleted": True},
                message="Produk berhasil dihapus"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
