"""
PPOB Product Service
Service untuk menangani operasi produk PPOB
"""

from typing import List, Optional
from fastapi import HTTPException, status

from app.common.base_classes.base_service import BaseService
from app.domains.ppob.repositories.ppob_repository import PPOBRepository
from app.domains.ppob.models.ppob import PPOBProduct, PPOBCategory

try:
    from app.cache.managers.ppob_cache_manager import ppob_cache_manager
except ImportError:
    ppob_cache_manager = None


class PPOBProductService(BaseService):
    """Service untuk menangani operasi produk PPOB"""
    
    def __init__(self, repository: PPOBRepository):
        super().__init__(repository)
    
    async def get_products_by_category(self, category: PPOBCategory) -> List[PPOBProduct]:
        """Ambil produk berdasarkan kategori"""
        try:
            # Check cache first
            if ppob_cache_manager:
                cache_key = f"products_category_{category.code}"
                cached_products = await ppob_cache_manager.get(cache_key)
                if cached_products:
                    return cached_products
            
            products = await self.repository.get_products_by_category(category.id)
            
            # Cache the result
            if ppob_cache_manager and products:
                await ppob_cache_manager.set(cache_key, products, ttl=300)  # 5 minutes
            
            return products
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting products: {str(e)}"
            )
    
    async def get_product_by_code(self, product_code: str) -> Optional[PPOBProduct]:
        """Ambil produk berdasarkan kode"""
        try:
            # Check cache first
            if ppob_cache_manager:
                cache_key = f"product_{product_code}"
                cached_product = await ppob_cache_manager.get(cache_key)
                if cached_product:
                    return cached_product
            
            product = await self.repository.get_product_by_code(product_code)
            
            # Cache the result
            if ppob_cache_manager and product:
                await ppob_cache_manager.set(cache_key, product, ttl=600)  # 10 minutes
            
            return product
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting product: {str(e)}"
            )
    
    async def get_all_categories(self) -> List[PPOBCategory]:
        """Ambil semua kategori produk"""
        try:
            # Check cache first
            if ppob_cache_manager:
                cache_key = "ppob_categories"
                cached_categories = await ppob_cache_manager.get(cache_key)
                if cached_categories:
                    return cached_categories
            
            categories = await self.repository.get_all_categories()
            
            # Cache the result
            if ppob_cache_manager and categories:
                await ppob_cache_manager.set(cache_key, categories, ttl=1800)  # 30 minutes
            
            return categories
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting categories: {str(e)}"
            )
    
    async def search_products(self, query: str, category_id: Optional[int] = None) -> List[PPOBProduct]:
        """Cari produk berdasarkan query"""
        try:
            products = await self.repository.search_products(query, category_id)
            return products
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching products: {str(e)}"
            )
    
    async def get_popular_products(self, limit: int = 10) -> List[PPOBProduct]:
        """Ambil produk populer"""
        try:
            # Check cache first
            if ppob_cache_manager:
                cache_key = f"popular_products_{limit}"
                cached_products = await ppob_cache_manager.get(cache_key)
                if cached_products:
                    return cached_products
            
            products = await self.repository.get_popular_products(limit)
            
            # Cache the result
            if ppob_cache_manager and products:
                await ppob_cache_manager.set(cache_key, products, ttl=900)  # 15 minutes
            
            return products
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting popular products: {str(e)}"
            )
