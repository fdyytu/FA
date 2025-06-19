from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from decimal import Decimal as PyDecimal

from app.core.database import Base
import enum
from typing import Optional

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TransactionType(enum.Enum):
    PPOB = "ppob"
    WALLET_TOPUP = "wallet_topup"
    WALLET_TRANSFER = "wallet_transfer"
    VOUCHER_PURCHASE = "voucher_purchase"
    PRODUCT_PURCHASE = "product_purchase"

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True)  # Could be Discord user ID or internal user ID
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Financial details
    amount = Column(Numeric(15, 2), nullable=False)
    fee = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="IDR")
    
    # Transaction details
    description = Column(Text)
    reference_id = Column(String(100))  # External reference (e.g., PPOB transaction ID)
    payment_method = Column(String(50))
    
    # Metadata
    extra_data = Column(Text)  # JSON string for additional data
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, transaction_id={self.transaction_id}, type={self.transaction_type}, status={self.status})>"

class TransactionLog(Base):
    __tablename__ = "transaction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), ForeignKey("transactions.transaction_id"), nullable=False)
    status_from = Column(SQLEnum(TransactionStatus))
    status_to = Column(SQLEnum(TransactionStatus), nullable=False)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    transaction = relationship("Transaction", backref="logs")
    
    def __repr__(self):
        return f"<TransactionLog(transaction_id={self.transaction_id}, {self.status_from} -> {self.status_to})>"
