from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.domains.voucher.models.voucher import VoucherType, VoucherStatus

class VoucherBase(BaseModel):
    """Base schema untuk voucher"""
    code: str = Field(..., description="Kode voucher unik")
    name: str = Field(..., description="Nama voucher")
    description: Optional[str] = None
    voucher_type: VoucherType = Field(..., description="Tipe voucher")
    discount_value: Decimal = Field(..., description="Nilai diskon")
    max_discount: Optional[Decimal] = None
    min_transaction: Decimal = Field(default=Decimal('0'))
    usage_limit: Optional[int] = None
    user_limit: int = Field(default=1)
    valid_from: datetime = Field(..., description="Berlaku dari")
    valid_until: datetime = Field(..., description="Berlaku sampai")
    applicable_categories: Optional[List[str]] = None
    applicable_products: Optional[List[str]] = None

class VoucherCreate(VoucherBase):
    """Schema untuk membuat voucher baru"""
    
    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('Tanggal berakhir harus setelah tanggal mulai')
        return v
    
    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if 'voucher_type' in values:
            if values['voucher_type'] == VoucherType.PERCENTAGE and v > 100:
                raise ValueError('Persentase diskon tidak boleh lebih dari 100%')
            if v <= 0:
                raise ValueError('Nilai diskon harus lebih dari 0')
        return v

class VoucherUpdate(BaseModel):
    """Schema untuk update voucher"""
    name: Optional[str] = None
    description: Optional[str] = None
    discount_value: Optional[Decimal] = None
    max_discount: Optional[Decimal] = None
    min_transaction: Optional[Decimal] = None
    usage_limit: Optional[int] = None
    user_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    status: Optional[VoucherStatus] = None
    applicable_categories: Optional[List[str]] = None
    applicable_products: Optional[List[str]] = None

class VoucherResponse(VoucherBase):
    """Schema response untuk voucher"""
    id: int
    status: VoucherStatus
    usage_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VoucherValidationRequest(BaseModel):
    """Schema request untuk validasi voucher"""
    code: str = Field(..., description="Kode voucher")
    transaction_amount: Decimal = Field(..., description="Jumlah transaksi")
    category: Optional[str] = None
    product_code: Optional[str] = None

class VoucherValidationResponse(BaseModel):
    """Schema response untuk validasi voucher"""
    valid: bool
    voucher_id: Optional[int] = None
    discount_amount: Decimal = Field(default=Decimal('0'))
    final_amount: Decimal
    message: str

class VoucherUsageResponse(BaseModel):
    """Schema response untuk penggunaan voucher"""
    id: int
    voucher_code: str
    voucher_name: str
    discount_amount: Decimal
    original_amount: Decimal
    final_amount: Decimal
    used_at: datetime
    
    class Config:
        from_attributes = True

class VoucherStatsResponse(BaseModel):
    """Schema response untuk statistik voucher"""
    total_vouchers: int
    active_vouchers: int
    expired_vouchers: int
    total_usage: int
    total_discount_given: float
