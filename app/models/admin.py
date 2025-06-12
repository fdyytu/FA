from sqlalchemy import Column, String, Numeric, Boolean, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class MarginType(enum.Enum):
    PERCENTAGE = "percentage"
    NOMINAL = "nominal"

class Admin(BaseModel):
    """Model untuk admin - mengikuti prinsip Single Responsibility"""
    __tablename__ = "admins"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superadmin = Column(Boolean, default=False)
    phone_number = Column(String(20), nullable=True)
    
    # Relationships
    notification_settings = relationship("AdminNotificationSetting", back_populates="admin")

class AdminConfig(BaseModel):
    """Model untuk konfigurasi admin"""
    __tablename__ = "admin_configs"
    
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    config_value = Column(Text, nullable=False)
    config_type = Column(String(50), default="string")  # string, number, boolean, encrypted
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

class PPOBMarginConfig(BaseModel):
    """Model untuk konfigurasi margin PPOB"""
    __tablename__ = "ppob_margin_configs"
    
    category = Column(String(50), nullable=False)  # kategori PPOB atau 'global'
    product_code = Column(String(50), nullable=True)  # null untuk margin global kategori
    margin_type = Column(Enum(MarginType), nullable=False)
    margin_value = Column(Numeric(15, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
