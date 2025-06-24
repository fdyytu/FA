from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Tuple
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import ProductManagementRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import ProductCreate, ProductUpdate
from app.domains.ppob.models.ppob import PPOBProduct


class ProductCrudService(BaseService):
    """Service untuk operasi CRUD produk - Single Responsibility: Product CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductManagementRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_products(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[PPOBProduct], int]:
        """Ambil daftar produk dengan filter"""
        return self.product_repo.get_products_with_pagination(
            skip, limit, search, category, is_active
        )
    
    def get_product_categories(self) -> List[str]:
        """Ambil semua kategori produk"""
        return self.product_repo.get_product_categories()
    
    def create_product(self, product_data: ProductCreate, admin_id: str) -> PPOBProduct:
        """Buat produk baru"""
        product = PPOBProduct(
            product_code=product_data.product_code,
            product_name=product_data.product_name,
            category=product_data.category,
            price=product_data.price,
            admin_fee=product_data.admin_fee,
            description=product_data.description,
            is_active="1" if product_data.is_active else "0"
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="CREATE",
            resource="product",
            resource_id=product.id,
            new_values=json.dumps(product_data.dict(), default=str)
        )
        
        return product
    
    def update_product(
        self,
        product_id: str,
        product_data: ProductUpdate,
        admin_id: str
    ) -> PPOBProduct:
        """Update produk"""
        product = self.db.query(PPOBProduct).filter(PPOBProduct.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "product_name": product.product_name,
            "price": str(product.price),
            "admin_fee": str(product.admin_fee),
            "description": product.description,
            "is_active": product.is_active
        }
        
        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "is_active":
                setattr(product, field, "1" if value else "0")
            else:
                setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="product",
            resource_id=product_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data, default=str)
        )
        
        return product
