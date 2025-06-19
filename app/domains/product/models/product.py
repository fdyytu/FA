from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.common.base_classes.base import BaseModel
import enum

class ProductStatus(enum.Enum):
    """Status produk"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"

class ProductType(enum.Enum):
    """Tipe produk"""
    PREPAID = "prepaid"
    POSTPAID = "postpaid"
    VOUCHER = "voucher"

class Product(BaseModel):
    """
    Model untuk produk PPOB.
    Mengimplementasikan Single Responsibility Principle.
    """
    __tablename__ = "products"
    
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    product_type = Column(Enum(ProductType), default=ProductType.PREPAID)
    base_price = Column(Numeric(15, 2), nullable=False)
    selling_price = Column(Numeric(15, 2), nullable=False)
    admin_fee = Column(Numeric(15, 2), default=0)
    margin = Column(Numeric(15, 2), default=0)
    status = Column(Enum(ProductStatus), default=ProductStatus.ACTIVE)
    description = Column(Text, nullable=True)
    min_denomination = Column(Numeric(15, 2), nullable=True)
    max_denomination = Column(Numeric(15, 2), nullable=True)
    stock_available = Column(Boolean, default=True)
    daily_limit = Column(Integer, nullable=True)
    monthly_limit = Column(Integer, nullable=True)
    
    # Relationships will be added when related models are properly configured
    # transactions = relationship("PPOBTransaction", back_populates="product")
