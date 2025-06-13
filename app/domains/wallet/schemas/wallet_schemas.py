from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum
from app.domains.wallet.models.wallet import (
    TransactionType, TransactionStatus, PaymentMethod, TopUpStatus
)

class TransactionTypeEnum(str, Enum):
    """Enum untuk tipe transaksi"""
    TOPUP_MANUAL = "topup_manual"
    TOPUP_MIDTRANS = "topup_midtrans"
    TRANSFER_SEND = "transfer_send"
    TRANSFER_RECEIVE = "transfer_receive"
    PPOB_PAYMENT = "ppob_payment"
    REFUND = "refund"

class TransactionStatusEnum(str, Enum):
    """Enum untuk status transaksi"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethodEnum(str, Enum):
    """Enum untuk metode pembayaran"""
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    MIDTRANS = "midtrans"

class TopUpStatusEnum(str, Enum):
    """Enum untuk status top up"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Wallet Balance Response
class WalletBalanceResponse(BaseModel):
    """Schema response untuk saldo wallet"""
    balance: Decimal = Field(..., description="Saldo wallet saat ini")
    user_id: int = Field(..., description="ID user")
    username: str = Field(..., description="Username")
    
    class Config:
        from_attributes = True

# Wallet Transaction Schemas
class WalletTransactionBase(BaseModel):
    """Base schema untuk transaksi wallet"""
    amount: Decimal = Field(..., gt=0, description="Jumlah transaksi harus positif")
    description: Optional[str] = Field(None, description="Deskripsi transaksi")

class WalletTransactionCreate(WalletTransactionBase):
    """Schema untuk membuat transaksi wallet baru"""
    transaction_type: TransactionTypeEnum = Field(..., description="Tipe transaksi")
    reference_id: Optional[str] = Field(None, description="ID referensi eksternal")
    metadata: Optional[str] = Field(None, description="Metadata tambahan")

class WalletTransactionUpdate(BaseModel):
    """Schema untuk update transaksi wallet"""
    status: Optional[TransactionStatusEnum] = None
    description: Optional[str] = None
    reference_id: Optional[str] = None
    metadata: Optional[str] = None

class WalletTransactionResponse(BaseModel):
    """Schema response untuk transaksi wallet"""
    id: int
    transaction_code: str
    transaction_type: TransactionTypeEnum
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    status: TransactionStatusEnum
    description: Optional[str]
    reference_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Transfer Schemas
class TransferRequest(BaseModel):
    """Schema request untuk transfer"""
    receiver_username: str = Field(..., description="Username penerima")
    amount: Decimal = Field(..., gt=0, description="Jumlah transfer harus positif")
    description: Optional[str] = Field(None, description="Deskripsi transfer")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Jumlah harus lebih besar dari 0')
        if v > 10000000:  # 10 million limit
            raise ValueError('Jumlah melebihi batas maksimum')
        return v
    
    @validator('receiver_username')
    def validate_receiver_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Username penerima tidak valid')
        return v.strip()

class TransferResponse(BaseModel):
    """Schema response untuk transfer"""
    id: int
    transfer_code: str
    sender_username: str
    receiver_username: str
    amount: Decimal
    status: TransactionStatusEnum
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Top Up Schemas
class TopUpManualRequest(BaseModel):
    """Schema request untuk top up manual"""
    amount: Decimal = Field(..., gt=0, description="Jumlah top up harus positif")
    payment_method: PaymentMethodEnum = Field(..., description="Metode pembayaran")
    bank_name: Optional[str] = Field(None, description="Nama bank")
    account_number: Optional[str] = Field(None, description="Nomor rekening")
    account_name: Optional[str] = Field(None, description="Nama pemilik rekening")
    notes: Optional[str] = Field(None, description="Catatan tambahan")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Jumlah harus lebih besar dari 0')
        if v < 10000:  # Minimum 10k
            raise ValueError('Jumlah minimum top up adalah 10.000')
        if v > 50000000:  # Maximum 50 million
            raise ValueError('Jumlah melebihi batas maksimum')
        return v

class TopUpMidtransRequest(BaseModel):
    """Schema request untuk top up Midtrans"""
    amount: Decimal = Field(..., gt=0, description="Jumlah top up harus positif")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Jumlah harus lebih besar dari 0')
        if v < 10000:  # Minimum 10k
            raise ValueError('Jumlah minimum top up adalah 10.000')
        if v > 50000000:  # Maximum 50 million
            raise ValueError('Jumlah melebihi batas maksimum')
        return v

class TopUpResponse(BaseModel):
    """Schema response untuk top up"""
    id: int
    request_code: str
    amount: Decimal
    payment_method: PaymentMethodEnum
    status: TopUpStatusEnum
    bank_name: Optional[str]
    account_number: Optional[str]
    account_name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TopUpMidtransResponse(BaseModel):
    """Schema response untuk top up Midtrans"""
    request_code: str
    amount: Decimal
    midtrans_order_id: str
    payment_url: str
    status: TopUpStatusEnum
    
    class Config:
        from_attributes = True

# Admin Schemas
class TopUpApprovalRequest(BaseModel):
    """Schema request untuk approval top up"""
    status: TopUpStatusEnum = Field(..., description="Status approval")
    admin_notes: Optional[str] = Field(None, description="Catatan admin")
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [TopUpStatusEnum.APPROVED, TopUpStatusEnum.REJECTED]:
            raise ValueError('Status harus approved atau rejected')
        return v

class TopUpListResponse(BaseModel):
    """Schema response untuk daftar top up"""
    id: int
    request_code: str
    user_username: str
    amount: Decimal
    payment_method: PaymentMethodEnum
    status: TopUpStatusEnum
    bank_name: Optional[str]
    account_number: Optional[str]
    account_name: Optional[str]
    proof_image: Optional[str]
    notes: Optional[str]
    admin_notes: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Transaction History
class TransactionHistoryResponse(BaseModel):
    """Schema response untuk riwayat transaksi"""
    transactions: List[WalletTransactionResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    
    class Config:
        from_attributes = True

# Statistics Schemas
class WalletStatsResponse(BaseModel):
    """Schema response untuk statistik wallet"""
    total_transactions: int = Field(..., description="Total transaksi")
    success_transactions: int = Field(..., description="Transaksi berhasil")
    failed_transactions: int = Field(..., description="Transaksi gagal")
    pending_transactions: int = Field(..., description="Transaksi pending")
    total_topup: float = Field(..., description="Total top up")
    total_transfer_out: float = Field(..., description="Total transfer keluar")
    today_transactions: int = Field(..., description="Transaksi hari ini")
    success_rate: float = Field(..., description="Tingkat keberhasilan (%)")

class MonthlyTransactionSummaryResponse(BaseModel):
    """Schema response untuk ringkasan transaksi bulanan"""
    year: int = Field(..., description="Tahun")
    month: int = Field(..., description="Bulan")
    total_topup: float = Field(..., description="Total top up")
    total_transfer: float = Field(..., description="Total transfer")
    total_ppob: float = Field(..., description="Total PPOB")
    total_transactions: int = Field(..., description="Total transaksi")

# Midtrans Notification Schema
class MidtransNotificationRequest(BaseModel):
    """Schema untuk notifikasi Midtrans"""
    order_id: str
    status_code: str
    gross_amount: str
    signature_key: str
    transaction_status: str
    transaction_id: str
    payment_type: str
    fraud_status: Optional[str] = None
    
class MidtransNotificationResponse(BaseModel):
    """Schema response untuk notifikasi Midtrans"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
