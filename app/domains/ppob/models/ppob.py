from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.shared.base_classes.base import BaseModel
import enum

class TransactionStatus(enum.Enum):
    """Status transaksi PPOB"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PPOBCategory(enum.Enum):
    """Kategori layanan PPOB"""
    PULSA = "pulsa"
    LISTRIK = "listrik"
    PDAM = "pdam"
    INTERNET = "internet"
    BPJS = "bpjs"
    MULTIFINANCE = "multifinance"

class PPOBTransaction(BaseModel):
    """
    Model untuk transaksi PPOB.
    Mengimplementasikan Single Responsibility Principle - hanya menangani data transaksi PPOB.
    """
    __tablename__ = "ppob_transactions"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transaction_code = Column(String(50), unique=True, index=True, nullable=False)
    category = Column(Enum(PPOBCategory), nullable=False)
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    customer_number = Column(String(50), nullable=False)
    customer_name = Column(String(100), nullable=True)
    amount = Column(Numeric(15, 2), nullable=False)
    admin_fee = Column(Numeric(15, 2), default=0)
    total_amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    provider_ref = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationship will be added when User model is properly configured
    # user = relationship("User", back_populates="ppob_transactions")

class PPOBProduct(BaseModel):
    """
    Model untuk produk PPOB.
    Menyimpan informasi produk yang tersedia untuk transaksi PPOB.
    """
    __tablename__ = "ppob_products"
    
    product_code = Column(String(50), unique=True, index=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(Enum(PPOBCategory), nullable=False)
    provider = Column(String(50), nullable=False)
    price = Column(Numeric(15, 2), nullable=False)
    admin_fee = Column(Numeric(15, 2), default=0)
    is_active = Column(String(10), default="1")
    description = Column(Text, nullable=True)
