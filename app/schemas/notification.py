from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class NotificationTypeEnum(str, Enum):
    """Enum untuk jenis notifikasi"""
    TRANSACTION = "transaction"
    SYSTEM = "system"
    PROMOTION = "promotion"
    SECURITY = "security"

class NotificationChannelEnum(str, Enum):
    """Enum untuk channel notifikasi"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    DISCORD = "discord"
    PUSH = "push"
    SMS = "sms"

class NotificationStatusEnum(str, Enum):
    """Enum untuk status notifikasi"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class NotificationBase(BaseModel):
    """Base schema untuk notifikasi"""
    title: str
    message: str
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    metadata: Optional[str] = None

class NotificationCreate(NotificationBase):
    """Schema untuk membuat notifikasi baru"""
    user_id: Optional[int] = None  # Null untuk notifikasi admin

class NotificationUpdate(BaseModel):
    """Schema untuk update notifikasi"""
    status: Optional[NotificationStatusEnum] = None
    is_read: Optional[bool] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    """Schema untuk response notifikasi"""
    id: int
    user_id: Optional[int]
    status: NotificationStatusEnum
    is_read: bool
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AdminNotificationSettingBase(BaseModel):
    """Base schema untuk pengaturan notifikasi admin"""
    notification_type: NotificationTypeEnum
    channel: NotificationChannelEnum
    is_enabled: bool = True
    webhook_url: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class AdminNotificationSettingCreate(AdminNotificationSettingBase):
    """Schema untuk membuat pengaturan notifikasi admin"""
    admin_id: int

class AdminNotificationSettingUpdate(BaseModel):
    """Schema untuk update pengaturan notifikasi admin"""
    is_enabled: Optional[bool] = None
    webhook_url: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class AdminNotificationSettingResponse(AdminNotificationSettingBase):
    """Schema untuk response pengaturan notifikasi admin"""
    id: int
    admin_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WebhookLogBase(BaseModel):
    """Base schema untuk log webhook"""
    webhook_type: str
    request_method: str
    request_url: str
    request_headers: Optional[str] = None
    request_body: Optional[str] = None
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    processed: bool = False
    error_message: Optional[str] = None

class WebhookLogCreate(WebhookLogBase):
    """Schema untuk membuat log webhook"""
    pass

class WebhookLogResponse(WebhookLogBase):
    """Schema untuk response log webhook"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NotificationSendRequest(BaseModel):
    """Schema untuk request kirim notifikasi"""
    title: str
    message: str
    notification_type: NotificationTypeEnum
    channels: List[NotificationChannelEnum]
    user_ids: Optional[List[int]] = None  # Null untuk broadcast ke admin
    metadata: Optional[str] = None
