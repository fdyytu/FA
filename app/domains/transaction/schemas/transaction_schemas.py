from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.domains.transaction.models.transaction import TransactionStatus, TransactionType

class TransactionBase(BaseModel):
    transaction_type: TransactionType
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    description: Optional[str] = None
    reference_id: Optional[str] = None
    payment_method: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: int
    fee: Optional[Decimal] = Field(default=0, ge=0)
    
    class Config:
        json_encoders = {
            Decimal: str
        }

class TransactionUpdate(BaseModel):
    status: Optional[TransactionStatus] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class TransactionResponse(TransactionBase):
    id: int
    transaction_id: str
    user_id: int
    status: TransactionStatus
    fee: Decimal
    total_amount: Decimal
    currency: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None
        }

class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

class TransactionLogResponse(BaseModel):
    id: int
    transaction_id: str
    status_from: Optional[TransactionStatus]
    status_to: TransactionStatus
    message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class TransactionStatsResponse(BaseModel):
    total_transactions: int
    total_amount: Decimal
    successful_transactions: int
    failed_transactions: int
    pending_transactions: int
    
    class Config:
        json_encoders = {
            Decimal: str
        }
