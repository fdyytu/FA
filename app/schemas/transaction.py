from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TransactionTypeEnum(str, Enum):
    """Enum untuk jenis transaksi"""
    PPOB = "ppob"
    TOPUP = "topup"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"

class TransactionStatusEnum(str, Enum):
    """Enum untuk status transaksi"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionBase(BaseModel):
    """Base schema untuk transaksi"""
    transaction_type: TransactionTypeEnum
    amount: float
    admin_fee: float = 0
    description: Optional[str] = None
    reference_id: Optional[str] = None
    metadata: Optional[str] = None

class TransactionCreate(TransactionBase):
    """Schema untuk membuat transaksi baru"""
    user_id: int

class TransactionUpdate(BaseModel):
    """Schema untuk update transaksi"""
    status: Optional[TransactionStatusEnum] = None
    reference_id: Optional[str] = None
    metadata: Optional[str] = None
    processed_at: Optional[datetime] = None

class TransactionResponse(TransactionBase):
    """Schema untuk response transaksi"""
    id: int
    user_id: int
    transaction_code: str
    total_amount: float
    status: TransactionStatusEnum
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TransactionHistoryResponse(BaseModel):
    """Schema untuk riwayat transaksi"""
    id: int
    transaction_code: str
    transaction_type: TransactionTypeEnum
    amount: float
    admin_fee: float
    total_amount: float
    status: TransactionStatusEnum
    description: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class DailyMutationResponse(BaseModel):
    """Schema untuk mutasi harian"""
    id: int
    mutation_date: datetime
    total_transactions: int
    total_amount: float
    total_fee: float
    success_count: int
    failed_count: int
    pending_count: int
    transaction_types: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionSummaryResponse(BaseModel):
    """Schema untuk ringkasan transaksi"""
    total_transactions: int
    total_amount: float
    total_fee: float
    success_rate: float
    transaction_by_type: Dict[str, int]
    transaction_by_status: Dict[str, int]

class TransactionFilterRequest(BaseModel):
    """Schema untuk filter transaksi"""
    user_id: Optional[int] = None
    transaction_type: Optional[TransactionTypeEnum] = None
    status: Optional[TransactionStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    limit: int = 10
