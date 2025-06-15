from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AdminRole(str, Enum):
    """Admin role enum untuk API"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"

class MarginType(str, Enum):
    """Margin type enum untuk API"""
    PERCENTAGE = "percentage"
    NOMINAL = "nominal"

# Base schemas
class AdminBase(BaseModel):
    """Base schema untuk admin - DRY principle"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    role: AdminRole = AdminRole.ADMIN

class AdminCreate(AdminBase):
    """Schema untuk membuat admin baru"""
    password: str = Field(..., min_length=8)

class AdminUpdate(BaseModel):
    """Schema untuk update admin - Interface Segregation"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None

class AdminResponse(AdminBase):
    """Schema response admin"""
    id: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    """Schema untuk login admin"""
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    """Schema response login admin"""
    access_token: str
    token_type: str = "bearer"
    admin: AdminResponse

# User Management Schemas
class UserManagementResponse(BaseModel):
    """Schema untuk response user management"""
    id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    balance: float
    phone_number: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserUpdateByAdmin(BaseModel):
    """Schema untuk update user oleh admin"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    balance: Optional[float] = Field(None, ge=0)

# Product Management Schemas
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

# Configuration Schemas
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

# Margin Configuration Schemas
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

# Dashboard Schemas
class DashboardStats(BaseModel):
    """Schema untuk statistik dashboard"""
    total_users: int
    active_users: int
    total_transactions: int
    total_revenue: float
    pending_transactions: int
    failed_transactions: int

class TransactionStats(BaseModel):
    """Schema untuk statistik transaksi"""
    date: str
    count: int
    amount: float

class DashboardResponse(BaseModel):
    """Schema response dashboard"""
    stats: DashboardStats
    recent_transactions: List[Dict[str, Any]]
    transaction_trends: List[TransactionStats]
    top_products: List[Dict[str, Any]]

# Provider Management Schemas
class ProviderConfig(BaseModel):
    """Schema untuk konfigurasi provider"""
    provider_name: str
    is_active: bool
    priority: int = Field(..., ge=1)
    config: Dict[str, Any]

class ProviderResponse(BaseModel):
    """Schema response provider"""
    provider_name: str
    is_active: bool
    priority: int
    status: str  # healthy, unhealthy, unknown
    last_check: Optional[datetime]

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    """Schema response audit log"""
    id: str
    admin_username: str
    action: str
    resource: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Pagination Schemas
class PaginationParams(BaseModel):
    """Schema untuk parameter pagination - DRY principle"""
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class PaginatedResponse(BaseModel):
    """Schema untuk response dengan pagination"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Discord Configuration Schemas untuk Admin
class DiscordConfigCreate(BaseModel):
    """Schema untuk membuat konfigurasi Discord baru"""
    name: str = Field(..., min_length=1, max_length=100, description="Nama konfigurasi")
    token: str = Field(..., min_length=50, description="Discord bot token")
    guild_id: Optional[str] = Field(None, description="Discord Guild ID")
    command_prefix: str = Field("!", max_length=10, description="Command prefix untuk bot")
    is_active: bool = Field(True, description="Status aktif konfigurasi")

class DiscordConfigUpdate(BaseModel):
    """Schema untuk update konfigurasi Discord"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    token: Optional[str] = Field(None, min_length=50)
    guild_id: Optional[str] = None
    command_prefix: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None

class DiscordConfigResponse(BaseModel):
    """Schema untuk response konfigurasi Discord"""
    id: int
    name: str
    token: str  # Will be masked in response
    guild_id: Optional[str]
    command_prefix: str
    is_active: bool
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
