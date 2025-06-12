from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.admin import MarginType
from decimal import Decimal

class AdminConfigBase(BaseModel):
    config_key: str = Field(..., description="Kunci konfigurasi")
    config_value: str = Field(..., description="Nilai konfigurasi")
    config_type: str = Field(default="string", description="Tipe konfigurasi")
    description: Optional[str] = Field(None, description="Deskripsi konfigurasi")
    is_active: bool = Field(default=True, description="Status aktif")

class AdminConfigCreate(AdminConfigBase):
    pass

class AdminConfigUpdate(BaseModel):
    config_value: Optional[str] = None
    config_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AdminConfigResponse(AdminConfigBase):
    id: int
    
    class Config:
        from_attributes = True

class PPOBMarginConfigBase(BaseModel):
    category: str = Field(..., description="Kategori PPOB")
    product_code: Optional[str] = Field(None, description="Kode produk (opsional)")
    margin_type: MarginType = Field(..., description="Tipe margin")
    margin_value: Decimal = Field(..., description="Nilai margin")
    is_active: bool = Field(default=True, description="Status aktif")
    description: Optional[str] = Field(None, description="Deskripsi")

class PPOBMarginConfigCreate(PPOBMarginConfigBase):
    pass

class PPOBMarginConfigUpdate(BaseModel):
    margin_type: Optional[MarginType] = None
    margin_value: Optional[Decimal] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None

class PPOBMarginConfigResponse(PPOBMarginConfigBase):
    id: int
    
    class Config:
        from_attributes = True

class DigiflazzConfigRequest(BaseModel):
    username: str = Field(..., description="Username Digiflazz")
    api_key: str = Field(..., description="API Key Digiflazz")
    production: bool = Field(default=False, description="Mode production")

class DigiflazzConfigResponse(BaseModel):
    username: str
    production: bool
    is_configured: bool
    
class MarginConfigRequest(BaseModel):
    category: str = Field(..., description="Kategori PPOB atau 'global'")
    product_code: Optional[str] = Field(None, description="Kode produk spesifik")
    margin_type: MarginType = Field(..., description="Tipe margin (percentage/nominal)")
    margin_value: Decimal = Field(..., description="Nilai margin")
    description: Optional[str] = Field(None, description="Deskripsi")
