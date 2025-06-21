from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)

class ProductController:
    """
    Controller untuk manajemen produk - Single Responsibility: Product management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen produk"""
        
        @self.router.get("/", response_model=dict)
        async def get_products(
            skip: int = 0,
            limit: int = 100,
            category: Optional[str] = None,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil daftar produk"""
            try:
                # Mock data untuk produk
                products = [
                    {
                        "id": f"prod_{i}",
                        "name": f"Product {i}",
                        "description": f"Description for product {i}",
                        "price": 10000 + (i * 1000),
                        "category": "electronics" if i % 2 == 0 else "clothing",
                        "stock": 100 - i,
                        "is_active": True,
                        "created_at": "2025-01-16T10:00:00Z",
                        "updated_at": "2025-01-16T10:00:00Z"
                    }
                    for i in range(1, min(limit + 1, 21))
                ]
                
                # Apply category filter if provided
                if category:
                    products = [p for p in products if p["category"] == category]
                
                # Apply pagination
                total = len(products)
                products = products[skip:skip + limit]
                
                return {
                    "success": True,
                    "data": {
                        "products": products,
                        "total": total,
                        "skip": skip,
                        "limit": limit
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting products: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil daftar produk: {str(e)}"
                )
        
        @self.router.get("/{product_id}", response_model=dict)
        async def get_product(
            product_id: str,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil detail produk"""
            try:
                # Mock data untuk detail produk
                product = {
                    "id": product_id,
                    "name": f"Product {product_id}",
                    "description": f"Detailed description for product {product_id}",
                    "price": 15000,
                    "category": "electronics",
                    "stock": 50,
                    "is_active": True,
                    "specifications": {
                        "weight": "1.2kg",
                        "dimensions": "20x15x5cm",
                        "warranty": "1 year"
                    },
                    "images": [
                        f"https://example.com/images/{product_id}_1.jpg",
                        f"https://example.com/images/{product_id}_2.jpg"
                    ],
                    "created_at": "2025-01-16T10:00:00Z",
                    "updated_at": "2025-01-16T10:00:00Z"
                }
                
                return {
                    "success": True,
                    "data": product
                }
                
            except Exception as e:
                logger.error(f"Error getting product {product_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil detail produk: {str(e)}"
                )
        
        @self.router.get("/categories/list", response_model=dict)
        async def get_product_categories(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil daftar kategori produk"""
            try:
                categories = [
                    {
                        "id": "electronics",
                        "name": "Electronics",
                        "description": "Electronic devices and gadgets",
                        "product_count": 150
                    },
                    {
                        "id": "clothing",
                        "name": "Clothing",
                        "description": "Fashion and apparel",
                        "product_count": 200
                    },
                    {
                        "id": "books",
                        "name": "Books",
                        "description": "Books and educational materials",
                        "product_count": 75
                    }
                ]
                
                return {
                    "success": True,
                    "data": {
                        "categories": categories,
                        "total": len(categories)
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting product categories: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Gagal mengambil kategori produk: {str(e)}"
                )

# Initialize controller
product_controller = ProductController()

# Export router untuk kompatibilitas dengan import
router = product_controller.router
