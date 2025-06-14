from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.shared.base_classes.base import BaseModel
import enum
from datetime import datetime

class VoucherType(enum.Enum):
    """Tipe voucher"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_ADMIN_FEE = "free_admin_fee"

class VoucherStatus(enum.Enum):
    """Status voucher"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"

class Voucher(BaseModel):
    """
    Model untuk voucher/promo.
    Mengimplementasikan Single Responsibility Principle.
    """
    __tablename__ = "vouchers"
    
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    voucher_type = Column(Enum(VoucherType), nullable=False)
    discount_value = Column(Numeric(15, 2), nullable=False)
    max_discount = Column(Numeric(15, 2), nullable=True)
    min_transaction = Column(Numeric(15, 2), default=0)
    usage_limit = Column(Integer, nullable=True)
    usage_count = Column(Integer, default=0)
    user_limit = Column(Integer, default=1)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    status = Column(Enum(VoucherStatus), default=VoucherStatus.ACTIVE)
    applicable_categories = Column(Text, nullable=True)  # JSON string
    applicable_products = Column(Text, nullable=True)  # JSON string
    
    # Relationships
    usages = relationship("VoucherUsage", back_populates="voucher")

class VoucherUsage(BaseModel):
    """
    Model untuk penggunaan voucher.
    Tracking siapa yang sudah menggunakan voucher.
    """
    __tablename__ = "voucher_usages"
    
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("ppob_transactions.id"), nullable=True)
    discount_amount = Column(Numeric(15, 2), nullable=False)
    original_amount = Column(Numeric(15, 2), nullable=False)
    final_amount = Column(Numeric(15, 2), nullable=False)
    
    # Relationships
    voucher = relationship("Voucher", back_populates="usages")
    user = relationship("User", back_populates="voucher_usages")
    transaction = relationship("PPOBTransaction", back_populates="voucher_usage")
