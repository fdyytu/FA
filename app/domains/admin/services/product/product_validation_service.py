from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.common.base_classes.base_service import BaseService
from app.domains.admin.schemas.admin_schemas import ProductCreate
from app.domains.ppob.models.ppob import PPOBProduct


class ProductValidationService(BaseService):
    """Service untuk validasi produk - Single Responsibility: Product validation logic"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def validate_product_code_unique(self, product_code: str, exclude_id: Optional[str] = None) -> bool:
        """Validasi apakah kode produk unik"""
        query = self.db.query(PPOBProduct).filter(PPOBProduct.product_code == product_code)
        
        if exclude_id:
            query = query.filter(PPOBProduct.id != exclude_id)
        
        existing_product = query.first()
        
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kode produk sudah digunakan"
            )
        
        return True
    
    def validate_product_data(self, product_data: ProductCreate) -> bool:
        """Validasi data produk sebelum create/update"""
        # Validasi kode produk
        self.validate_product_code_unique(product_data.product_code)
        
        # Validasi harga
        if product_data.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Harga produk harus lebih dari 0"
            )
        
        # Validasi admin fee
        if product_data.admin_fee < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin fee tidak boleh negatif"
            )
        
        # Validasi nama produk
        if not product_data.product_name or len(product_data.product_name.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nama produk minimal 3 karakter"
            )
        
        # Validasi kategori
        if not product_data.category or len(product_data.category.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kategori produk minimal 2 karakter"
            )
        
        return True
    
    def validate_product_exists(self, product_id: str) -> PPOBProduct:
        """Validasi apakah produk ada"""
        product = self.db.query(PPOBProduct).filter(PPOBProduct.id == product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        return product
    
    def validate_product_can_be_deleted(self, product_id: str) -> bool:
        """Validasi apakah produk bisa dihapus"""
        product = self.validate_product_exists(product_id)
        
        # Cek apakah produk sedang digunakan dalam transaksi aktif
        # TODO: Implementasi pengecekan transaksi aktif
        # Untuk saat ini, semua produk bisa dihapus
        
        return True
