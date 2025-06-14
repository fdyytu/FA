from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    """Base schema untuk produk"""
    name: str = Field(..., min_length=1, max_length=200, description="Nama produk")
    slug: str = Field(..., min_length=1, max_length=250, description="URL slug produk")
    description: Optional[str] = Field(None, description="Deskripsi lengkap produk")
    short_description: Optional[str] = Field(None, max_length=500, description="Deskripsi singkat produk")
    category: str = Field(..., description="Kategori produk")
    subcategory: Optional[str] = Field(None, description="Sub-kategori produk")
    tags: Optional[List[str]] = Field(None, description="Tags produk")
    price: Decimal = Field(..., gt=0, description="Harga produk")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="Harga modal")
    compare_at_price: Optional[Decimal] = Field(None, ge=0, description="Harga pembanding")
    sku: Optional[str] = Field(None, max_length=100, description="SKU produk")
    stock_quantity: int = Field(0, ge=0, description="Jumlah stok")
    track_inventory: bool = Field(True, description="Track inventory")
    allow_backorder: bool = Field(False, description="Izinkan backorder")
    weight: Optional[Decimal] = Field(None, ge=0, description="Berat produk (kg)")
    dimensions: Optional[str] = Field(None, description="Dimensi produk")
    meta_title: Optional[str] = Field(None, max_length=200, description="Meta title SEO")
    meta_description: Optional[str] = Field(None, max_length=500, description="Meta description SEO")
    featured_image: Optional[str] = Field(None, description="URL gambar utama")
    gallery_images: Optional[List[str]] = Field(None, description="URL gambar galeri")
    is_featured: bool = Field(False, description="Produk unggulan")
    is_digital: bool = Field(False, description="Produk digital")
    requires_shipping: bool = Field(True, description="Memerlukan pengiriman")

class ProductCreate(ProductBase):
    """Schema untuk membuat produk baru"""
    pass

class ProductUpdate(BaseModel):
    """Schema untuk update produk"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    compare_at_price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    allow_backorder: Optional[bool] = None
    weight: Optional[Decimal] = Field(None, ge=0)
    dimensions: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    featured_image: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_digital: Optional[bool] = None
    requires_shipping: Optional[bool] = None
    status: Optional[str] = None

class ProductResponse(ProductBase):
    """Schema response untuk produk"""
    id: int
    status: str
    view_count: int
    purchase_count: int
    rating_average: Decimal
    rating_count: int
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    """Schema response untuk list produk"""
    id: int
    name: str
    slug: str
    short_description: Optional[str]
    category: str
    price: Decimal
    compare_at_price: Optional[Decimal]
    featured_image: Optional[str]
    status: str
    is_featured: bool
    stock_quantity: int
    rating_average: Decimal
    rating_count: int
    
    class Config:
        from_attributes = True

class VoucherBase(BaseModel):
    """Base schema untuk voucher"""
    code: str = Field(..., min_length=1, max_length=50, description="Kode voucher")
    name: str = Field(..., min_length=1, max_length=200, description="Nama voucher")
    description: Optional[str] = Field(None, description="Deskripsi voucher")
    voucher_type: str = Field(..., description="Tipe voucher (percentage, fixed_amount, etc.)")
    discount_value: Decimal = Field(..., gt=0, description="Nilai diskon")
    max_discount_amount: Optional[Decimal] = Field(None, ge=0, description="Maksimal diskon")
    minimum_order_amount: Optional[Decimal] = Field(None, ge=0, description="Minimal order")
    maximum_order_amount: Optional[Decimal] = Field(None, ge=0, description="Maksimal order")
    usage_limit: Optional[int] = Field(None, ge=1, description="Limit penggunaan total")
    usage_limit_per_user: Optional[int] = Field(None, ge=1, description="Limit per user")
    valid_from: datetime = Field(..., description="Berlaku dari")
    valid_until: datetime = Field(..., description="Berlaku sampai")
    applicable_products: Optional[List[int]] = Field(None, description="Produk yang berlaku")
    applicable_categories: Optional[List[str]] = Field(None, description="Kategori yang berlaku")
    excluded_products: Optional[List[int]] = Field(None, description="Produk yang dikecualikan")
    applicable_users: Optional[List[int]] = Field(None, description="User yang berlaku")
    new_users_only: bool = Field(False, description="Hanya untuk user baru")
    is_public: bool = Field(True, description="Voucher publik")

    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_until must be after valid_from')
        return v

class VoucherCreate(VoucherBase):
    """Schema untuk membuat voucher baru"""
    pass

class VoucherUpdate(BaseModel):
    """Schema untuk update voucher"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    discount_value: Optional[Decimal] = Field(None, gt=0)
    max_discount_amount: Optional[Decimal] = Field(None, ge=0)
    minimum_order_amount: Optional[Decimal] = Field(None, ge=0)
    maximum_order_amount: Optional[Decimal] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_user: Optional[int] = Field(None, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_products: Optional[List[int]] = None
    applicable_categories: Optional[List[str]] = None
    excluded_products: Optional[List[int]] = None
    applicable_users: Optional[List[int]] = None
    new_users_only: Optional[bool] = None
    is_public: Optional[bool] = None
    status: Optional[str] = None

class VoucherResponse(VoucherBase):
    """Schema response untuk voucher"""
    id: int
    current_usage_count: int
    status: str
    usage_count: int
    total_discount_given: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VoucherValidationRequest(BaseModel):
    """Schema untuk validasi voucher"""
    code: str = Field(..., description="Kode voucher")
    user_id: int = Field(..., description="ID user")
    order_amount: Decimal = Field(..., gt=0, description="Total order")
    product_ids: Optional[List[int]] = Field(None, description="ID produk dalam order")

class VoucherValidationResponse(BaseModel):
    """Schema response validasi voucher"""
    is_valid: bool
    discount_amount: Decimal
    message: str
    voucher_id: Optional[int] = None
    voucher_name: Optional[str] = None

class VoucherUsageCreate(BaseModel):
    """Schema untuk mencatat penggunaan voucher"""
    voucher_id: int = Field(..., description="ID voucher")
    user_id: int = Field(..., description="ID user")
    order_id: Optional[int] = Field(None, description="ID order")
    discount_amount: Decimal = Field(..., gt=0, description="Jumlah diskon")
    order_amount: Decimal = Field(..., gt=0, description="Total order")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")

class VoucherUsageResponse(BaseModel):
    """Schema response untuk voucher usage"""
    id: int
    voucher_id: int
    user_id: int
    order_id: Optional[int]
    discount_amount: Decimal
    order_amount: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductFilter(BaseModel):
    """Schema untuk filter produk"""
    category: Optional[str] = Field(None, description="Filter berdasarkan kategori")
    subcategory: Optional[str] = Field(None, description="Filter berdasarkan sub-kategori")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Harga minimum")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Harga maksimum")
    is_featured: Optional[bool] = Field(None, description="Filter produk unggulan")
    status: Optional[str] = Field(None, description="Filter berdasarkan status")
    search: Optional[str] = Field(None, description="Pencarian berdasarkan nama/deskripsi")
    sort_by: Optional[str] = Field("created_at", description="Urutkan berdasarkan")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Urutan sort")

class VoucherFilter(BaseModel):
    """Schema untuk filter voucher"""
    voucher_type: Optional[str] = Field(None, description="Filter berdasarkan tipe")
    status: Optional[str] = Field(None, description="Filter berdasarkan status")
    is_public: Optional[bool] = Field(None, description="Filter voucher publik")
    valid_now: Optional[bool] = Field(None, description="Filter voucher yang berlaku sekarang")
    search: Optional[str] = Field(None, description="Pencarian berdasarkan kode/nama")
    sort_by: Optional[str] = Field("created_at", description="Urutkan berdasarkan")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Urutan sort")
