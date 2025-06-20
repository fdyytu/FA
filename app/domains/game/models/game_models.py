"""
Model untuk produk gaming dan validasi akun game
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class GameCategory(Base):
    """Model untuk kategori game"""
    __tablename__ = "game_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    icon = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    products = relationship("GameProduct", back_populates="category")

class GameProduct(Base):
    """Model untuk produk game spesifik"""
    __tablename__ = "game_products"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("game_categories.id"))
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    margin = Column(Float, default=0.0)
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    validation_required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    category = relationship("GameCategory", back_populates="products")

class GameValidation(Base):
    """Model untuk validasi akun game"""
    __tablename__ = "game_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    game_code = Column(String(50), nullable=False)
    user_id = Column(String(100), nullable=False)
    server_id = Column(String(50))
    nickname = Column(String(100))
    is_valid = Column(Boolean, default=False)
    validation_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
