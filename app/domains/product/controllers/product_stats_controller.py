from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.common.responses.api_response import APIResponse
from app.domains.product.services.product_service import ProductService
from app.domains.product.schemas.product_schemas import ProductStatsResponse
from app.api.deps import get_db, get_current_user
from app.domains.auth.models.user import User

class ProductStatsController:
    """
    Product Stats Controller - menangani operasi statistik dan analytics produk
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/products", tags=["Product Statistics"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk statistik produk"""
        
        self.router.add_api_route(
            "/stats",
            self.get_product_stats,
            methods=["GET"],
            response_model=APIResponse[ProductStatsResponse]
        )
        self.router.add_api_route(
            "/stats/categories",
            self.get_category_stats,
            methods=["GET"],
            response_model=APIResponse[dict]
        )
        self.router.add_api_route(
            "/stats/providers",
            self.get_provider_stats,
            methods=["GET"],
            response_model=APIResponse[dict]
        )
        self.router.add_api_route(
            "/popular",
            self.get_popular_products,
            methods=["GET"],
            response_model=APIResponse[List[dict]]
        )
        self.router.add_api_route(
            "/low-stock",
            self.get_low_stock_products,
            methods=["GET"],
            response_model=APIResponse[List[dict]]
        )
    
    async def get_product_stats(
        self,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[ProductStatsResponse]:
        """Ambil statistik umum produk"""
        try:
            product_service = ProductService(db)
            stats = await product_service.get_product_stats()
            
            return APIResponse.success(
                data=stats,
                message="Statistik produk berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_category_stats(
        self,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[dict]:
        """Ambil statistik berdasarkan kategori"""
        try:
            product_service = ProductService(db)
            stats = await product_service.get_category_stats()
            
            return APIResponse.success(
                data=stats,
                message="Statistik kategori berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_provider_stats(
        self,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[dict]:
        """Ambil statistik berdasarkan provider"""
        try:
            product_service = ProductService(db)
            stats = await product_service.get_provider_stats()
            
            return APIResponse.success(
                data=stats,
                message="Statistik provider berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_popular_products(
        self,
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db)
    ) -> APIResponse[List[dict]]:
        """Ambil produk populer berdasarkan jumlah transaksi"""
        try:
            product_service = ProductService(db)
            products = await product_service.get_popular_products(limit)
            
            return APIResponse.success(
                data=products,
                message=f"Top {len(products)} produk populer"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_low_stock_products(
        self,
        threshold: int = Query(10, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[List[dict]]:
        """Ambil produk dengan stok rendah"""
        try:
            product_service = ProductService(db)
            products = await product_service.get_low_stock_products(threshold, limit)
            
            return APIResponse.success(
                data=products,
                message=f"Produk dengan stok di bawah {threshold}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_revenue_by_product(
        self,
        start_date: Optional[str] = Query(None),
        end_date: Optional[str] = Query(None),
        limit: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ) -> APIResponse[List[dict]]:
        """Ambil revenue berdasarkan produk dalam periode tertentu"""
        try:
            product_service = ProductService(db)
            revenue_data = await product_service.get_revenue_by_product(
                start_date, end_date, limit
            )
            
            return APIResponse.success(
                data=revenue_data,
                message="Data revenue per produk berhasil diambil"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
