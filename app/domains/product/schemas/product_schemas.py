from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.domains.product.models.product import ProductStatus, ProductType

class ProductBase(BaseModel):
    """Base schema untuk produk"""
    code: str = Field(..., description="Kode produk unik")
    name: str = Field(..., description="Nama produk")
    category: str = Field(..., description="Kategori produk")
    provider: str = Field(..., description="Provider layanan")
    product_type: ProductType = Field(default=ProductType.PREPAID)
    base_price: Decimal = Field(..., description="Harga dasar")
    selling_price: Decimal = Field(..., description="Harga jual")
    admin_fee: Decimal = Field(default=Decimal('0'))
    margin: Decimal = Field(default=Decimal('0'))
    description: Optional[str] = None
    min_denomination: Optional[Decimal] = None
    max_denomination: Optional[Decimal] = None
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None

class ProductCreate(ProductBase):
    """Schema untuk membuat produk baru"""
    
    @validator('selling_price')
    def validate_selling_price(cls, v, values):
        if 'base_price' in values and v < values['base_price']:
            raise ValueError('Harga jual tidak boleh lebih kecil dari harga dasar')
        return v

class ProductUpdate(BaseModel):
    """Schema untuk update produk"""
    name: Optional[str] = None
    base_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    admin_fee: Optional[Decimal] = None
    margin: Optional[Decimal] = None
    status: Optional[ProductStatus] = None
    description: Optional[str] = None
    stock_available: Optional[bool] = None
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None

class ProductResponse(ProductBase):
    """Schema response untuk produk"""
    id: int
    status: ProductStatus
    stock_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """Schema response untuk list produk"""
    products: List[ProductResponse]
    total: int
    page: int
    size: int

class ProductStatsResponse(BaseModel):
    """Schema response untuk statistik produk"""
    total_products: int
    active_products: int
    inactive_products: int
    categories: List[str]
    providers: List[str]
