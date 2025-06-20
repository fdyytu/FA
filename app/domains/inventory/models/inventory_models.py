"""
Model untuk manajemen stok dan inventory
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StockAlert(Base):
    """Model untuk alert stok"""
    __tablename__ = "stock_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    product_type = Column(String(50), nullable=False)  # game, ppob, etc
    current_stock = Column(Integer, nullable=False)
    min_stock = Column(Integer, nullable=False)
    alert_level = Column(String(20), default="warning")  # warning, critical, empty
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

class StockMovement(Base):
    """Model untuk tracking pergerakan stok"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    product_type = Column(String(50), nullable=False)
    movement_type = Column(String(20), nullable=False)  # in, out, adjustment
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)
    reference_id = Column(String(100))  # transaction_id, purchase_id, etc
    notes = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class StockReservation(Base):
    """Model untuk reservasi stok sementara"""
    __tablename__ = "stock_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)
    product_type = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    reserved_for = Column(String(100), nullable=False)  # user_id, order_id
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime)
