from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime
import enum

class NotificationType(enum.Enum):
    """Jenis notifikasi"""
    TRANSACTION = "transaction"
    SYSTEM = "system"
    PROMOTION = "promotion"
    SECURITY = "security"

class NotificationChannel(enum.Enum):
    """Channel notifikasi"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    DISCORD = "discord"
    PUSH = "push"
    SMS = "sms"

class NotificationStatus(enum.Enum):
    """Status notifikasi"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class Notification(BaseModel):
    """Model untuk notifikasi - mengikuti prinsip Single Responsibility"""
    __tablename__ = "notifications"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null untuk notifikasi admin
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON untuk data tambahan
    
    # Relationship
    user = relationship("User", back_populates="notifications")

class AdminNotificationSetting(BaseModel):
    """Pengaturan notifikasi untuk admin"""
    __tablename__ = "admin_notification_settings"
    
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    channel = Column(Enum(NotificationChannel), nullable=False)
    is_enabled = Column(Boolean, default=True)
    webhook_url = Column(String(500), nullable=True)  # Untuk Discord webhook
    phone_number = Column(String(20), nullable=True)  # Untuk WhatsApp
    email = Column(String(100), nullable=True)  # Untuk email
    
    # Relationship
    admin = relationship("Admin", back_populates="notification_settings")

class WebhookLog(BaseModel):
    """Log untuk webhook Digiflazz dan lainnya"""
    __tablename__ = "webhook_logs"
    
    webhook_type = Column(String(50), nullable=False)  # digiflazz, midtrans, etc
    request_method = Column(String(10), nullable=False)
    request_url = Column(String(500), nullable=False)
    request_headers = Column(Text, nullable=True)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
