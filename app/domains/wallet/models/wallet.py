from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.shared.base_classes.base import BaseModel
import enum
from datetime import datetime

class TransactionType(enum.Enum):
    """Tipe transaksi wallet"""
    TOPUP_MANUAL = "topup_manual"
    TOPUP_MIDTRANS = "topup_midtrans"
    TRANSFER_SEND = "transfer_send"
    TRANSFER_RECEIVE = "transfer_receive"
    PPOB_PAYMENT = "ppob_payment"
    REFUND = "refund"

class TransactionStatus(enum.Enum):
    """Status transaksi"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentMethod(enum.Enum):
    """Metode pembayaran"""
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    MIDTRANS = "midtrans"

class TopUpStatus(enum.Enum):
    """Status top up"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class WalletTransaction(BaseModel):
    """
    Model untuk transaksi wallet.
    Mengimplementasikan Single Responsibility Principle - hanya menangani data transaksi wallet.
    """
    __tablename__ = "wallet_transactions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_code = Column(String(50), unique=True, index=True, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    balance_before = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)  # For external references
    meta_data = Column(Text, nullable=True)  # JSON string for additional data
    
    # Relationship
    user = relationship("User", back_populates="wallet_transactions")

class Transfer(BaseModel):
    """
    Model untuk transfer antar user.
    Menyimpan informasi transfer uang antar pengguna.
    """
    __tablename__ = "transfers"
    
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transfer_code = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(Text, nullable=True)
    sender_transaction_id = Column(Integer, ForeignKey("wallet_transactions.id"), nullable=True)
    receiver_transaction_id = Column(Integer, ForeignKey("wallet_transactions.id"), nullable=True)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_transfers")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_transfers")

class TopUpRequest(BaseModel):
    """
    Model untuk permintaan top up.
    Menyimpan informasi permintaan pengisian saldo wallet.
    """
    __tablename__ = "topup_requests"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_code = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(TopUpStatus), default=TopUpStatus.PENDING)
    bank_name = Column(String(50), nullable=True)
    account_number = Column(String(50), nullable=True)
    account_name = Column(String(100), nullable=True)
    proof_image = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    midtrans_order_id = Column(String(100), nullable=True)
    midtrans_transaction_id = Column(String(100), nullable=True)
    wallet_transaction_id = Column(Integer, ForeignKey("wallet_transactions.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="topup_requests")
    processed_by_user = relationship("User", foreign_keys=[processed_by])
