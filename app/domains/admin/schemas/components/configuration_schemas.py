"""
Configuration schemas - dipecah dari admin_schemas.py
Berisi schema untuk configuration management
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MarginType(str, Enum):
    """Margin type enum untuk API"""
    PERCENTAGE = "percentage"
    NOMINAL = "nominal"


class ConfigCreate(BaseModel):
    """Schema untuk membuat konfigurasi"""
    config_key: str = Field(..., min_length=1, max_length=100)
    config_value: str
    config_type: str = Field("string", pattern="^(string|number|boolean|encrypted)$")
    description: Optional[str] = None


class ConfigUpdate(BaseModel):
    """Schema untuk update konfigurasi"""
    config_value: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ConfigResponse(BaseModel):
    """Schema response konfigurasi"""
    id: str
    config_key: str
    config_value: str
    config_type: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MarginConfigCreate(BaseModel):
    """Schema untuk membuat konfigurasi margin"""
    category: str = Field(..., min_length=1, max_length=50)
    product_code: Optional[str] = Field(None, max_length=50)
    margin_type: MarginType
    margin_value: float = Field(..., ge=0)
    description: Optional[str] = None


class MarginConfigUpdate(BaseModel):
    """Schema untuk update konfigurasi margin"""
    margin_type: Optional[MarginType] = None
    margin_value: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MarginConfigResponse(BaseModel):
    """Schema response konfigurasi margin"""
    id: str
    category: str
    product_code: Optional[str]
    margin_type: MarginType
    margin_value: float
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
