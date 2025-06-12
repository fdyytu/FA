from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
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

# Schema baru untuk fitur user yang lengkap

class UserPasswordChange(BaseModel):
    """Schema untuk ganti password"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password minimal 8 karakter')
        if not any(c.isupper() for c in v):
            raise ValueError('Password harus mengandung huruf besar')
        if not any(c.islower() for c in v):
            raise ValueError('Password harus mengandung huruf kecil')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password harus mengandung angka')
        return v

class UserSettingsUpdate(BaseModel):
    """Schema untuk update pengaturan user"""
    notifications: Optional[Dict[str, Any]] = None
    privacy: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    display: Optional[Dict[str, Any]] = None

class UserPreferences(BaseModel):
    """Schema untuk preferensi user"""
    dashboard: Optional[Dict[str, Any]] = None
    transactions: Optional[Dict[str, Any]] = None
    notifications: Optional[Dict[str, Any]] = None

class UserSecuritySettings(BaseModel):
    """Schema untuk pengaturan keamanan user"""
    two_factor_enabled: bool
    login_alerts: bool
    session_timeout: int
    last_password_change: datetime
    active_sessions: int
    login_history: List[Dict[str, Any]]

class UserActivityLog(BaseModel):
    """Schema untuk log aktivitas user"""
    id: int
    activity_type: str
    description: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

class UserSessionInfo(BaseModel):
    """Schema untuk informasi sesi user"""
    session_id: str
    ip_address: str
    user_agent: str
    location: Optional[str]
    last_activity: datetime
    is_current: bool

class UserVerificationRequest(BaseModel):
    """Schema untuk request verifikasi identitas"""
    identity_type: str  # ktp, passport, etc
    identity_number: str
    identity_image_url: str
    selfie_image_url: str

class UserNotificationSettings(BaseModel):
    """Schema untuk pengaturan notifikasi user"""
    email_notifications: bool = True
    push_notifications: bool = True
    transaction_alerts: bool = True
    marketing_emails: bool = False
    low_balance_alerts: bool = True
    security_alerts: bool = True

class UserPrivacySettings(BaseModel):
    """Schema untuk pengaturan privasi user"""
    profile_visibility: str = "public"  # public, friends, private
    show_balance: bool = False
    show_transaction_history: bool = False
    allow_friend_requests: bool = True
    show_online_status: bool = True

class UserDisplaySettings(BaseModel):
    """Schema untuk pengaturan tampilan user"""
    language: str = "id"
    timezone: str = "Asia/Jakarta"
    currency: str = "IDR"
    theme: str = "light"  # light, dark, auto
    date_format: str = "DD/MM/YYYY"
    number_format: str = "id-ID"

class UserStatsResponse(BaseModel):
    """Schema untuk statistik user"""
    total_transactions: int
    total_spent: float
    total_received: float
    favorite_category: Optional[str]
    monthly_spending: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]

class UserExportRequest(BaseModel):
    """Schema untuk request export data user"""
    data_types: List[str]  # profile, transactions, activities
    format: str = "csv"  # csv, json, pdf
    date_range: Optional[Dict[str, datetime]] = None

class UserFeedbackRequest(BaseModel):
    """Schema untuk feedback user"""
    category: str  # bug, feature, general
    subject: str
    message: str
    rating: Optional[int] = None  # 1-5
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating harus antara 1-5')
        return v

class UserSupportTicket(BaseModel):
    """Schema untuk tiket support user"""
    category: str
    priority: str = "medium"  # low, medium, high, urgent
    subject: str
    description: str
    attachments: Optional[List[str]] = None

class UserReferralInfo(BaseModel):
    """Schema untuk informasi referral user"""
    referral_code: str
    total_referrals: int
    successful_referrals: int
    referral_earnings: float
    referred_users: List[Dict[str, Any]]
