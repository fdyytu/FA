from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.common.responses.api_response import APIResponse
from app.domains.product.services.product_service import ProductService
from app.domains.product.schemas.product_schemas import ProductResponse
from app.api.deps import get_db

class ProductSearchController:
    """
    Product Search Controller - menangani operasi pencarian dan filter produk
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/products", tags=["Product Search"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk pencarian produk"""
        
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
        self.router.add_api_route(
            "/provider/{provider}",
            self.get_products_by_provider,
            methods=["GET"],
            response_model=APIResponse[List[ProductResponse]]
        )
        self.router.add_api_route(
            "/price-range",
            self.get_products_by_price_range,
            methods=["GET"],
            response_model=APIResponse[List[ProductResponse]]
        )
    
    async def search_products(
        self,
        q: str = Query(..., min_length=1, description="Search query"),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[ProductResponse]]:
        """Cari produk berdasarkan nama atau deskripsi"""
        try:
            product_service = ProductService(db)
            products = await product_service.search_products(q, skip, limit)
            
            product_responses = [ProductResponse.from_orm(p) for p in products]
            
            return APIResponse.success(
                data=product_responses,
                message=f"Ditemukan {len(product_responses)} produk"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_products_by_category(
        self,
        category: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[ProductResponse]]:
        """Ambil produk berdasarkan kategori"""
        try:
            product_service = ProductService(db)
            products = await product_service.get_products_by_category(category, skip, limit)
            
            product_responses = [ProductResponse.from_orm(p) for p in products]
            
            return APIResponse.success(
                data=product_responses,
                message=f"Produk kategori {category}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_product_by_code(
        self,
        code: str,
        db: Session = Depends(get_db)
    ) -> APIResponse[ProductResponse]:
        """Ambil produk berdasarkan kode"""
        try:
            product_service = ProductService(db)
            product = await product_service.get_product_by_code(code)
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk dengan kode tersebut tidak ditemukan"
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
    
    async def get_products_by_provider(
        self,
        provider: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[ProductResponse]]:
        """Ambil produk berdasarkan provider"""
        try:
            product_service = ProductService(db)
            products = await product_service.get_products_by_provider(provider, skip, limit)
            
            product_responses = [ProductResponse.from_orm(p) for p in products]
            
            return APIResponse.success(
                data=product_responses,
                message=f"Produk dari provider {provider}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_products_by_price_range(
        self,
        min_price: float = Query(0, ge=0),
        max_price: float = Query(..., gt=0),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[ProductResponse]]:
        """Ambil produk berdasarkan rentang harga"""
        try:
            if min_price >= max_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Harga minimum harus lebih kecil dari harga maksimum"
                )
            
            product_service = ProductService(db)
            products = await product_service.get_products_by_price_range(
                min_price, max_price, skip, limit
            )
            
            product_responses = [ProductResponse.from_orm(p) for p in products]
            
            return APIResponse.success(
                data=product_responses,
                message=f"Produk dengan harga {min_price} - {max_price}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
