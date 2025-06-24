"""
Common schemas - dipecah dari admin_schemas.py
Berisi schema umum yang digunakan di berbagai tempat
"""

from pydantic import BaseModel, Field
from typing import List, Any, Optional, Dict
from datetime import datetime


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
