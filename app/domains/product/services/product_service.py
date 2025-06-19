from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal
from app.common.base_classes.base_service import BaseService
from app.domains.product.repositories.product_repository import ProductRepository
from app.domains.product.models.product import Product, ProductStatus
from app.domains.product.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductListResponse, ProductStatsResponse
)

class ProductService(BaseService):
    """
    Service untuk menangani produk PPOB.
    Mengimplementasikan Single Responsibility Principle - hanya logika bisnis produk.
    """
    
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Buat produk baru"""
        # Validasi kode produk unik
        existing = self.repository.get_by_code(product_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kode produk sudah digunakan"
            )
        
        # Hitung margin otomatis
        margin = product_data.selling_price - product_data.base_price - product_data.admin_fee
        
        product_dict = product_data.dict()
        product_dict['margin'] = margin
        
        return self.repository.create(product_dict)
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        """Update produk"""
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        update_data = product_data.dict(exclude_unset=True)
        
        # Recalculate margin if prices updated
        if any(key in update_data for key in ['base_price', 'selling_price', 'admin_fee']):
            base_price = update_data.get('base_price', product.base_price)
            selling_price = update_data.get('selling_price', product.selling_price)
            admin_fee = update_data.get('admin_fee', product.admin_fee)
            update_data['margin'] = selling_price - base_price - admin_fee
        
        return self.repository.update(product_id, update_data)
    
    async def delete_product(self, product_id: int) -> bool:
        """Soft delete produk (set status DISCONTINUED)"""
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        self.repository.update(product_id, {"status": ProductStatus.DISCONTINUED})
        return True
    
    async def get_product_by_code(self, code: str) -> Optional[Product]:
        """Ambil produk berdasarkan kode"""
        return self.repository.get_by_code(code)
    
    async def get_products_by_category(self, category: str, active_only: bool = True) -> List[Product]:
        """Ambil produk berdasarkan kategori"""
        return self.repository.get_by_category(category, active_only)
    
    async def search_products(self, search_term: str, limit: int = 20) -> List[Product]:
        """Cari produk"""
        return self.repository.search_products(search_term, limit)
    
    async def get_products_paginated(
        self,
        page: int = 1,
        size: int = 20,
        category: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[ProductStatus] = None
    ) -> ProductListResponse:
        """Ambil produk dengan pagination"""
        skip = (page - 1) * size
        products, total = self.repository.get_products_paginated(
            skip=skip, limit=size, category=category, provider=provider, status=status
        )
        
        return ProductListResponse(
            products=products,
            total=total,
            page=page,
            size=size
        )
    
    async def get_product_stats(self) -> ProductStatsResponse:
        """Ambil statistik produk"""
        stats = self.repository.get_product_stats()
        return ProductStatsResponse(**stats)
    
    async def toggle_product_status(self, product_id: int) -> Product:
        """Toggle status produk (active/inactive)"""
        product = self.repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        new_status = ProductStatus.INACTIVE if product.status == ProductStatus.ACTIVE else ProductStatus.ACTIVE
        return self.repository.update(product_id, {"status": new_status})
    
    async def bulk_update_prices(self, updates: List[dict]) -> int:
        """Update harga beberapa produk sekaligus"""
        updated_count = 0
        for update in updates:
            product_id = update.get('product_id')
            new_price = update.get('selling_price')
            
            if product_id and new_price:
                try:
                    await self.update_product(product_id, ProductUpdate(selling_price=new_price))
                    updated_count += 1
                except HTTPException:
                    continue
        
        return updated_count
