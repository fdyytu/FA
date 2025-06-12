from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal

class ProductBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    price: Decimal
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None

class ProductStockBase(BaseModel):
    quantity: int
    file_name: Optional[str] = None
    file_content: Optional[str] = None
    notes: Optional[str] = None

class ProductStockCreate(ProductStockBase):
    product_id: int

class ProductStockUpdate(BaseModel):
    quantity: Optional[int] = None
    notes: Optional[str] = None

class ProductStockResponse(ProductStockBase):
    id: int
    product_id: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class ProductResponse(ProductBase):
    id: int
    created_at: str
    updated_at: str
    stocks: List[ProductStockResponse] = []
    
    class Config:
        from_attributes = True

class FileUploadRequest(BaseModel):
    product_id: int
    notes: Optional[str] = None

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str
