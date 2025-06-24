"""
Product management schemas - dipecah dari admin_schemas.py
Berisi schema untuk product management oleh admin
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema untuk membuat produk baru"""
    product_code: str = Field(..., min_length=1, max_length=50)
    product_name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    admin_fee: float = Field(0, ge=0)
    description: Optional[str] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Schema untuk update produk"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    admin_fee: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema response produk"""
    id: str
    product_code: str
    product_name: str
    category: str
    price: float
    admin_fee: float
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
