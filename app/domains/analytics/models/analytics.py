from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.shared.base_classes.base import BaseModel
from datetime import datetime
import enum

class AnalyticsEventType(enum.Enum):
    """Tipe event analytics"""
    PRODUCT_VIEW = "product_view"
    PRODUCT_PURCHASE = "product_purchase"
    VOUCHER_CREATED = "voucher_created"
    VOUCHER_USED = "voucher_used"
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    TRANSACTION_SUCCESS = "transaction_success"
    TRANSACTION_FAILED = "transaction_failed"

class AnalyticsEvent(BaseModel):
    """
    Model untuk menyimpan event analytics.
    Mengimplementasikan Single Responsibility Principle - hanya menangani data analytics.
    """
    __tablename__ = "analytics_events"
    
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    product_id = Column(Integer, nullable=True, index=True)
    voucher_id = Column(Integer, nullable=True, index=True)
    transaction_id = Column(Integer, nullable=True, index=True)
    
    # Event data
    event_data = Column(Text, nullable=True)  # JSON string untuk data tambahan
    amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="IDR")
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(Text, nullable=True)
    
    # Timestamp dengan timezone
    event_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes untuk performance
    __table_args__ = (
        Index('idx_analytics_event_type_timestamp', 'event_type', 'event_timestamp'),
        Index('idx_analytics_user_timestamp', 'user_id', 'event_timestamp'),
        Index('idx_analytics_product_timestamp', 'product_id', 'event_timestamp'),
    )

class ProductAnalytics(BaseModel):
    """
    Model untuk analytics produk yang diagregasi.
    Menyimpan statistik harian untuk performance yang lebih baik.
    """
    __tablename__ = "product_analytics"
    
    product_id = Column(Integer, nullable=False, index=True)
    product_name = Column(String(200), nullable=False)
    category = Column(String(50), nullable=True, index=True)
    
    # Statistik harian
    date = Column(DateTime, nullable=False, index=True)
    views_count = Column(Integer, default=0)
    purchases_count = Column(Integer, default=0)
    revenue = Column(Numeric(15, 2), default=0)
    
    # Conversion metrics
    conversion_rate = Column(Numeric(5, 4), default=0)  # views to purchases
    avg_order_value = Column(Numeric(15, 2), default=0)
    
    # Unique indexes
    __table_args__ = (
        Index('idx_product_analytics_unique', 'product_id', 'date', unique=True),
        Index('idx_product_analytics_category_date', 'category', 'date'),
    )

class VoucherAnalytics(BaseModel):
    """
    Model untuk analytics voucher yang diagregasi.
    """
    __tablename__ = "voucher_analytics"
    
    voucher_id = Column(Integer, nullable=False, index=True)
    voucher_code = Column(String(50), nullable=False)
    voucher_type = Column(String(50), nullable=True, index=True)
    
    # Statistik harian
    date = Column(DateTime, nullable=False, index=True)
    usage_count = Column(Integer, default=0)
    total_discount = Column(Numeric(15, 2), default=0)
    total_revenue_impact = Column(Numeric(15, 2), default=0)
    
    # Effectiveness metrics
    redemption_rate = Column(Numeric(5, 4), default=0)
    avg_discount_per_use = Column(Numeric(15, 2), default=0)
    
    # Unique indexes
    __table_args__ = (
        Index('idx_voucher_analytics_unique', 'voucher_id', 'date', unique=True),
        Index('idx_voucher_analytics_type_date', 'voucher_type', 'date'),
    )

class DashboardMetrics(BaseModel):
    """
    Model untuk menyimpan metrics dashboard yang sudah dihitung.
    Untuk performance dashboard yang lebih cepat.
    """
    __tablename__ = "dashboard_metrics"
    
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)  # daily, weekly, monthly
    date = Column(DateTime, nullable=False, index=True)
    
    # Metric values
    value = Column(Numeric(20, 4), nullable=False)
    previous_value = Column(Numeric(20, 4), nullable=True)
    percentage_change = Column(Numeric(10, 4), nullable=True)
    
    # Additional data
    metadata = Column(Text, nullable=True)  # JSON string untuk data tambahan
    
    # Unique constraint
    __table_args__ = (
        Index('idx_dashboard_metrics_unique', 'metric_name', 'metric_type', 'date', unique=True),
    )
