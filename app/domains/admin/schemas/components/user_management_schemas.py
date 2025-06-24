"""
User management schemas - dipecah dari admin_schemas.py
Berisi schema untuk user management oleh admin
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


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
