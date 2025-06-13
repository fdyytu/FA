from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.domains.ppob.models.ppob import PPOBCategory, TransactionStatus

class PPOBProductBase(BaseModel):
    product_code: str
    product_name: str
    category: PPOBCategory
    provider: str
    price: Decimal
    admin_fee: Decimal = Decimal('0')
    description: Optional[str] = None

class PPOBProductCreate(PPOBProductBase):
    pass

class PPOBProductResponse(PPOBProductBase):
    id: int
    is_active: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class PPOBTransactionBase(BaseModel):
    category: PPOBCategory
    product_code: str
    customer_number: str
    
    @validator('customer_number')
    def validate_customer_number(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nomor pelanggan tidak valid')
        return v

class PPOBTransactionCreate(PPOBTransactionBase):
    pass

class PPOBTransactionResponse(BaseModel):
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
    category: PPOBCategory
    customer_number: str

class PPOBInquiryResponse(BaseModel):
    customer_number: str
    customer_name: str
    amount: Decimal
    admin_fee: Decimal
    total_amount: Decimal
    product_name: str
    ref_id: Optional[str] = None

class PPOBPaymentRequest(BaseModel):
    category: PPOBCategory
    product_code: str
    customer_number: str
    ref_id: Optional[str] = None

class PPOBCategoryResponse(BaseModel):
    category: PPOBCategory
    products: List[PPOBProductResponse]

class TransactionHistoryResponse(BaseModel):
    transactions: List[PPOBTransactionResponse]
    total: int
    page: int
    size: int
