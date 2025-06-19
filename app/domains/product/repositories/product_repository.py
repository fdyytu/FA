from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.common.base_classes.base_repository import BaseRepository
from app.domains.product.models.product import Product, ProductStatus

class ProductRepository:
    """
    Repository untuk produk - mengikuti SRP.
    Hanya menangani operasi database untuk produk.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.model = Product
    
    def create(self, obj_data: dict) -> Product:
        """Buat produk baru"""
        product = Product(**obj_data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """Ambil produk berdasarkan ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_all(self) -> List[Product]:
        """Ambil semua produk"""
        return self.db.query(Product).all()
    
    def update(self, product_id: int, update_data: dict) -> Product:
        """Update produk"""
        product = self.get_by_id(product_id)
        if product:
            for key, value in update_data.items():
                setattr(product, key, value)
            self.db.commit()
            self.db.refresh(product)
        return product
    
    def delete(self, product_id: int) -> bool:
        """Hapus produk"""
        product = self.get_by_id(product_id)
        if product:
            self.db.delete(product)
            self.db.commit()
            return True
        return False
    
    def get_by_code(self, code: str) -> Optional[Product]:
        """Ambil produk berdasarkan kode"""
        return self.db.query(Product).filter(Product.code == code).first()
    
    def get_by_category(self, category: str, active_only: bool = True) -> List[Product]:
        """Ambil produk berdasarkan kategori"""
        query = self.db.query(Product).filter(Product.category == category)
        if active_only:
            query = query.filter(Product.status == ProductStatus.ACTIVE)
        return query.all()
    
    def get_by_provider(self, provider: str, active_only: bool = True) -> List[Product]:
        """Ambil produk berdasarkan provider"""
        query = self.db.query(Product).filter(Product.provider == provider)
        if active_only:
            query = query.filter(Product.status == ProductStatus.ACTIVE)
        return query.all()
    
    def search_products(self, search_term: str, limit: int = 20) -> List[Product]:
        """Cari produk berdasarkan nama atau kode"""
        return self.db.query(Product).filter(
            or_(
                Product.name.ilike(f"%{search_term}%"),
                Product.code.ilike(f"%{search_term}%")
            )
        ).filter(Product.status == ProductStatus.ACTIVE).limit(limit).all()
    
    def get_products_paginated(
        self, 
        skip: int = 0, 
        limit: int = 20,
        category: Optional[str] = None,
        provider: Optional[str] = None,
        status: Optional[ProductStatus] = None
    ) -> tuple[List[Product], int]:
        """Ambil produk dengan pagination dan filter"""
        query = self.db.query(Product)
        
        if category:
            query = query.filter(Product.category == category)
        if provider:
            query = query.filter(Product.provider == provider)
        if status:
            query = query.filter(Product.status == status)
        
        total = query.count()
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    def get_categories(self) -> List[str]:
        """Ambil semua kategori produk yang tersedia"""
        result = self.db.query(Product.category).distinct().all()
        return [row[0] for row in result]
    
    def get_providers(self) -> List[str]:
        """Ambil semua provider yang tersedia"""
        result = self.db.query(Product.provider).distinct().all()
        return [row[0] for row in result]
    
    def get_product_stats(self) -> dict:
        """Ambil statistik produk"""
        total = self.db.query(Product).count()
        active = self.db.query(Product).filter(Product.status == ProductStatus.ACTIVE).count()
        inactive = self.db.query(Product).filter(Product.status == ProductStatus.INACTIVE).count()
        
        return {
            "total_products": total,
            "active_products": active,
            "inactive_products": inactive,
            "categories": self.get_categories(),
            "providers": self.get_providers()
        }
    
    def bulk_update_status(self, product_ids: List[int], status: ProductStatus) -> int:
        """Update status beberapa produk sekaligus"""
        updated = self.db.query(Product).filter(
            Product.id.in_(product_ids)
        ).update({"status": status}, synchronize_session=False)
        self.db.commit()
        return updated
