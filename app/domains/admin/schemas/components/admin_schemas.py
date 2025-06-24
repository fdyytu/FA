"""
Admin schemas - dipecah dari admin_schemas.py
Berisi schema untuk admin management
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    """Admin role enum untuk API"""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


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
    id: int
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
