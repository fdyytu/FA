from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserProfileBase(BaseModel):
    """Base schema untuk profil user"""
    avatar_url: Optional[str] = None
    birth_date: Optional[datetime] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    identity_number: Optional[str] = None
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    """Schema untuk membuat profil user baru"""
    pass

class UserProfileUpdate(UserProfileBase):
    """Schema untuk update profil user"""
    pass

class UserProfileResponse(UserProfileBase):
    """Schema untuk response profil user"""
    id: int
    user_id: int
    identity_verified: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserDetailResponse(BaseModel):
    """Schema untuk detail user lengkap dengan profil"""
    id: int
    username: str
    email: str
    full_name: str
    phone_number: Optional[str]
    balance: float
    is_active: bool
    created_at: datetime
    profile: Optional[UserProfileResponse] = None
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Schema untuk list user (untuk admin)"""
    id: int
    username: str
    email: str
    full_name: str
    phone_number: Optional[str]
    balance: float
    is_active: bool
    created_at: datetime
    last_transaction_date: Optional[datetime] = None
    total_transactions: int = 0
    
    class Config:
        from_attributes = True
