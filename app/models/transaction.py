from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime
import enum

class TransactionType(enum.Enum):
    """Jenis transaksi"""
    PPOB = "ppob"
    TOPUP = "topup"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(enum.Enum):
    """Status transaksi"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Transaction(BaseModel):
    """Model untuk semua jenis transaksi - mengikuti prinsip Single Responsibility"""
    __tablename__ = "transactions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_code = Column(String(50), unique=True, index=True, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    admin_fee = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)  # ID dari provider eksternal
    extra_data = Column(Text, nullable=True)  # JSON untuk data tambahan
    processed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="transactions")

class UserProfile(BaseModel):
    """Model untuk profil user yang lebih detail"""
    __tablename__ = "user_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    avatar_url = Column(String(255), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(10), nullable=True)
    identity_number = Column(String(20), nullable=True)  # KTP/NIK
    identity_verified = Column(String(10), default="0")  # 0=belum, 1=sudah
    bank_account = Column(String(50), nullable=True)
    bank_name = Column(String(100), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="profile")

class DailyMutation(BaseModel):
    """Model untuk mutasi harian - mengikuti prinsip Single Responsibility"""
    __tablename__ = "daily_mutations"
    
    mutation_date = Column(DateTime, nullable=False, index=True)
    total_transactions = Column(Integer, default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    total_fee = Column(Numeric(15, 2), default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    pending_count = Column(Integer, default=0)
    transaction_types = Column(Text, nullable=True)  # JSON untuk breakdown per tipe
