from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Product(BaseModel):
    """Model untuk produk"""
    __tablename__ = "products"
    
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(15, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    stocks = relationship("ProductStock", back_populates="product")

class ProductStock(BaseModel):
    """Model untuk stock produk"""
    __tablename__ = "product_stocks"
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    file_name = Column(String(255), nullable=True)  # nama file yang diupload
    file_content = Column(Text, nullable=True)  # isi file untuk referensi
    notes = Column(Text, nullable=True)
    
    # Relationship
    product = relationship("Product", back_populates="stocks")
