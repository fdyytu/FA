from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class TransactionStatus(str, Enum):
    """Status untuk transaksi PPOB"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

class PPOBTransaction(Base):
    """Model untuk transaksi PPOB"""
    __tablename__ = "ppob_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    transaction_code = Column(String, unique=True, index=True)
    category = Column(String)
    product_code = Column(String)
    product_name = Column(String)
    customer_number = Column(String)
    customer_name = Column(String)
    amount = Column(Float)
    admin_fee = Column(Float, default=0)
    total_amount = Column(Float)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    provider_ref = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="ppob_transactions")

class PPOBProduct(Base):
    """Model untuk produk PPOB"""
    __tablename__ = "ppob_products"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    product_code = Column(String, unique=True, index=True)
    product_name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Float)
    admin_fee = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PPOBMarginConfig(Base):
    """Model untuk konfigurasi margin PPOB"""
    __tablename__ = "ppob_margin_configs"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    product_code = Column(String, nullable=True)
    margin_type = Column(String)  # percentage atau fixed
    margin_value = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
