from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.domains.ppob.models.ppob import PPOBCategory, TransactionStatus

class PPOBProductBase(BaseModel):
    """Base schema untuk produk PPOB"""
    product_code: str = Field(..., description="Kode produk unik")
    product_name: str = Field(..., description="Nama produk")
    category: PPOBCategory = Field(..., description="Kategori produk")
    provider: str = Field(..., description="Provider layanan")
    price: Decimal = Field(..., description="Harga produk")
    admin_fee: Decimal = Field(default=Decimal('0'), description="Biaya admin")
    description: Optional[str] = Field(None, description="Deskripsi produk")

class PPOBProductCreate(PPOBProductBase):
    """Schema untuk membuat produk PPOB baru"""
    pass

class PPOBProductUpdate(BaseModel):
    """Schema untuk update produk PPOB"""
    product_name: Optional[str] = None
    price: Optional[Decimal] = None
    admin_fee: Optional[Decimal] = None
    is_active: Optional[str] = None
    description: Optional[str] = None

class PPOBProductResponse(PPOBProductBase):
    """Schema response untuk produk PPOB"""
    id: int
    is_active: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PPOBTransactionBase(BaseModel):
    """Base schema untuk transaksi PPOB"""
    category: PPOBCategory = Field(..., description="Kategori layanan")
    product_code: str = Field(..., description="Kode produk")
    customer_number: str = Field(..., description="Nomor pelanggan")
    
    @validator('customer_number')
    def validate_customer_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nomor pelanggan tidak valid')
        return v

class PPOBTransactionCreate(PPOBTransactionBase):
    """Schema untuk membuat transaksi PPOB baru"""
    pass

class PPOBTransactionUpdate(BaseModel):
    """Schema untuk update transaksi PPOB"""
    status: Optional[TransactionStatus] = None
    provider_ref: Optional[str] = None
    notes: Optional[str] = None
    customer_name: Optional[str] = None

class PPOBTransactionResponse(BaseModel):
    """Schema response untuk transaksi PPOB"""
    id: int
    transaction_code: str
    category: PPOBCategory
    product_code: str
    product_name: str
    customer_number: str
    customer_name: Optional[str]
    amount: Decimal
    admin_fee: Decimal
    total_amount: Decimal
    status: TransactionStatus
    provider_ref: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PPOBInquiryRequest(BaseModel):
    """Schema request untuk inquiry tagihan"""
    category: PPOBCategory = Field(..., description="Kategori layanan")
    customer_number: str = Field(..., description="Nomor pelanggan")
    
    @validator('customer_number')
    def validate_customer_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nomor pelanggan tidak valid')
        return v

class PPOBInquiryResponse(BaseModel):
    """Schema response untuk inquiry tagihan"""
    customer_number: str = Field(..., description="Nomor pelanggan")
    customer_name: str = Field(..., description="Nama pelanggan")
    amount: Decimal = Field(..., description="Jumlah tagihan")
    admin_fee: Decimal = Field(..., description="Biaya admin")
    total_amount: Decimal = Field(..., description="Total yang harus dibayar")
    product_name: str = Field(..., description="Nama produk")
    ref_id: Optional[str] = Field(None, description="Reference ID dari provider")
    due_date: Optional[datetime] = Field(None, description="Tanggal jatuh tempo")
    period: Optional[str] = Field(None, description="Periode tagihan")

class PPOBPaymentRequest(BaseModel):
    """Schema request untuk pembayaran"""
    category: PPOBCategory = Field(..., description="Kategori layanan")
    product_code: str = Field(..., description="Kode produk")
    customer_number: str = Field(..., description="Nomor pelanggan")
    ref_id: Optional[str] = Field(None, description="Reference ID dari inquiry")
    
    @validator('customer_number')
    def validate_customer_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nomor pelanggan tidak valid')
        return v

class PPOBCategoryResponse(BaseModel):
    """Schema response untuk kategori PPOB"""
    value: str = Field(..., description="Nilai kategori")
    name: str = Field(..., description="Nama kategori")

class PPOBCategoryWithProducts(BaseModel):
    """Schema response untuk kategori dengan produk"""
    category: PPOBCategory
    products: List[PPOBProductResponse]

class TransactionHistoryResponse(BaseModel):
    """Schema response untuk riwayat transaksi"""
    transactions: List[PPOBTransactionResponse]
    total: int
    page: int
    size: int

class PPOBStatsResponse(BaseModel):
    """Schema response untuk statistik PPOB"""
    total_transactions: int = Field(..., description="Total transaksi")
    success_transactions: int = Field(..., description="Transaksi berhasil")
    failed_transactions: int = Field(..., description="Transaksi gagal")
    pending_transactions: int = Field(..., description="Transaksi pending")
    total_amount: float = Field(..., description="Total nilai transaksi")
    today_transactions: int = Field(..., description="Transaksi hari ini")
    success_rate: float = Field(..., description="Tingkat keberhasilan (%)")

class PopularProductResponse(BaseModel):
    """Schema response untuk produk populer"""
    product_code: str = Field(..., description="Kode produk")
    product_name: str = Field(..., description="Nama produk")
    category: str = Field(..., description="Kategori produk")
    transaction_count: int = Field(..., description="Jumlah transaksi")

class MonthlyRevenueResponse(BaseModel):
    """Schema response untuk revenue bulanan"""
    year: int = Field(..., description="Tahun")
    month: int = Field(..., description="Bulan")
    total_revenue: float = Field(..., description="Total revenue")
    total_transactions: int = Field(..., description="Total transaksi")

class PPOBProviderResponse(BaseModel):
    """Schema response untuk provider PPOB"""
    name: str = Field(..., description="Nama provider")
    is_active: bool = Field(..., description="Status aktif")
    supported_categories: List[str] = Field(..., description="Kategori yang didukung")
    config: Dict[str, Any] = Field(..., description="Konfigurasi provider")
