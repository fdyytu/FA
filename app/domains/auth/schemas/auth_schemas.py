from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class UserBase(BaseModel):
    """Base schema untuk User - mengimplementasikan DRY principle"""
    username: str
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    """Schema untuk membuat user baru"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password harus minimal 8 karakter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password harus mengandung minimal 1 angka')
        if not any(c.isupper() for c in v):
            raise ValueError('Password harus mengandung minimal 1 huruf besar')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username harus minimal 3 karakter')
        if not v.isalnum():
            raise ValueError('Username hanya boleh mengandung huruf dan angka')
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and not v.startswith('+'):
            if not v.startswith('0'):
                raise ValueError('Nomor telepon harus dimulai dengan 0 atau +')
        return v

class UserLogin(BaseModel):
    """Schema untuk login user"""
    username: str
    password: str

class UserResponse(UserBase):
    """Schema untuk response user data"""
    id: int
    is_active: bool
    is_superuser: bool
    balance: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Schema untuk update user data"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v and not v.startswith('+'):
            if not v.startswith('0'):
                raise ValueError('Nomor telepon harus dimulai dengan 0 atau +')
        return v

class PasswordChange(BaseModel):
    """Schema untuk mengubah password"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password baru harus minimal 8 karakter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password baru harus mengandung minimal 1 angka')
        if not any(c.isupper() for c in v):
            raise ValueError('Password baru harus mengandung minimal 1 huruf besar')
        return v
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Konfirmasi password tidak cocok')
        return v

class Token(BaseModel):
    """Schema untuk token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Schema untuk token data"""
    username: Optional[str] = None
    user_id: Optional[int] = None

class RefreshToken(BaseModel):
    """Schema untuk refresh token request"""
    refresh_token: str

class UserStats(BaseModel):
    """Schema untuk statistik user"""
    total_users: int
    active_users: int
    inactive_users: int
    new_users_today: int
    new_users_this_month: int
