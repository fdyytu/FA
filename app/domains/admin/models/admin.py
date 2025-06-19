from sqlalchemy import Column, String, Numeric, Boolean, Text, Enum, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.common.base_classes.base import BaseModel
import enum
from datetime import datetime

class MarginType(enum.Enum):
    """Enum untuk tipe margin - Interface Segregation"""
    PERCENTAGE = "percentage"
    NOMINAL = "nominal"

class AdminRole(enum.Enum):
    """Enum untuk role admin"""
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"

class Admin(BaseModel):
    """
    Model untuk admin - Single Responsibility: Mengelola data admin
    """
    __tablename__ = "admins"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(AdminRole), default=AdminRole.ADMIN)
    phone_number = Column(String(20), nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    notification_settings = relationship("AdminNotificationSetting", back_populates="admin")
    audit_logs = relationship("AdminAuditLog", back_populates="admin")

class AdminConfig(BaseModel):
    """
    Model untuk konfigurasi admin - Single Responsibility: Mengelola konfigurasi sistem
    """
    __tablename__ = "admin_configs"
    
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), default="string")  # string, number, boolean, encrypted
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class PPOBMarginConfig(BaseModel):
    __table_args__ = {'extend_existing': True}
    """
    Model untuk konfigurasi margin PPOB - Single Responsibility: Mengelola margin pricing
    """
    __tablename__ = "ppob_margin_configs"
    
    category = Column(String(50), nullable=False)  # kategori PPOB atau 'global'
    product_code = Column(String(50), nullable=True)  # null untuk margin global kategori
    margin_type = Column(Enum(MarginType), nullable=False)
    margin_value = Column(Numeric(15, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)

class AdminAuditLog(BaseModel):
    """
    Model untuk audit log admin - Single Responsibility: Tracking admin activities
    """
    __tablename__ = "admin_audit_logs"
    
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    resource_id = Column(String(50), nullable=True)
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    admin = relationship("Admin", back_populates="audit_logs")

class AdminNotificationSetting(BaseModel):
    """
    Model untuk pengaturan notifikasi admin
    """
    __tablename__ = "admin_notification_settings"
    
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, default=True)
    
    # Relationships
    admin = relationship("Admin", back_populates="notification_settings")
