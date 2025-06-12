from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class TransactionTypeEnum(str, Enum):
    TOPUP_MANUAL = "topup_manual"
    TOPUP_MIDTRANS = "topup_midtrans"
    TRANSFER_SEND = "transfer_send"
    TRANSFER_RECEIVE = "transfer_receive"
    PPOB_PAYMENT = "ppob_payment"
    REFUND = "refund"

class TransactionStatusEnum(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethodEnum(str, Enum):
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    MIDTRANS = "midtrans"

class TopUpStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Wallet Balance Response
class WalletBalanceResponse(BaseModel):
    balance: Decimal
    user_id: int
    username: str
    
    class Config:
        from_attributes = True

# Wallet Transaction Schemas
class WalletTransactionBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Transaction amount must be positive")
    description: Optional[str] = None

class WalletTransactionCreate(WalletTransactionBase):
    transaction_type: TransactionTypeEnum
    reference_id: Optional[str] = None
    metadata: Optional[str] = None

class WalletTransactionResponse(BaseModel):
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
    
    class Config:
        from_attributes = True

# Transfer Schemas
class TransferRequest(BaseModel):
    receiver_username: str = Field(..., description="Username of the receiver")
    amount: Decimal = Field(..., gt=0, description="Transfer amount must be positive")
    description: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v > 10000000:  # 10 million limit
            raise ValueError('Amount exceeds maximum limit')
        return v

class TransferResponse(BaseModel):
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
    amount: Decimal = Field(..., gt=0, description="Top up amount must be positive")
    payment_method: PaymentMethodEnum
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v < 10000:  # Minimum 10k
            raise ValueError('Minimum top up amount is 10,000')
        if v > 50000000:  # Maximum 50 million
            raise ValueError('Amount exceeds maximum limit')
        return v

class TopUpMidtransRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Top up amount must be positive")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        if v < 10000:  # Minimum 10k
            raise ValueError('Minimum top up amount is 10,000')
        if v > 50000000:  # Maximum 50 million
            raise ValueError('Amount exceeds maximum limit')
        return v

class TopUpResponse(BaseModel):
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
    request_code: str
    amount: Decimal
    midtrans_order_id: str
    payment_url: str
    status: TopUpStatusEnum
    
    class Config:
        from_attributes = True

# Admin Schemas
class TopUpApprovalRequest(BaseModel):
    status: TopUpStatusEnum = Field(..., description="Approval status")
    admin_notes: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [TopUpStatusEnum.APPROVED, TopUpStatusEnum.REJECTED]:
            raise ValueError('Status must be either approved or rejected')
        return v

class TopUpListResponse(BaseModel):
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
    transactions: List[WalletTransactionResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int
    
    class Config:
        from_attributes = True
