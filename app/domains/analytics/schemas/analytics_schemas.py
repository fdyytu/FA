from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

class AnalyticsEventCreate(BaseModel):
    """Schema untuk membuat event analytics baru"""
    event_type: str = Field(..., description="Tipe event analytics")
    user_id: Optional[int] = Field(None, description="ID user yang melakukan event")
    session_id: Optional[str] = Field(None, description="Session ID")
    product_id: Optional[int] = Field(None, description="ID produk terkait")
    voucher_id: Optional[int] = Field(None, description="ID voucher terkait")
    transaction_id: Optional[int] = Field(None, description="ID transaksi terkait")
    event_data: Optional[Dict[str, Any]] = Field(None, description="Data tambahan event")
    amount: Optional[Decimal] = Field(None, description="Jumlah uang terkait event")
    ip_address: Optional[str] = Field(None, description="IP address user")
    user_agent: Optional[str] = Field(None, description="User agent browser")
    referrer: Optional[str] = Field(None, description="Referrer URL")

class AnalyticsEventResponse(BaseModel):
    """Schema response untuk event analytics"""
    id: int
    event_type: str
    user_id: Optional[int]
    session_id: Optional[str]
    product_id: Optional[int]
    voucher_id: Optional[int]
    transaction_id: Optional[int]
    amount: Optional[Decimal]
    currency: str
    ip_address: Optional[str]
    event_timestamp: datetime
    
    class Config:
        from_attributes = True

class ProductAnalyticsResponse(BaseModel):
    """Schema response untuk analytics produk"""
    id: int
    product_id: int
    product_name: str
    category: Optional[str]
    date: datetime
    views_count: int
    purchases_count: int
    revenue: Decimal
    conversion_rate: Decimal
    avg_order_value: Decimal
    
    class Config:
        from_attributes = True

class VoucherAnalyticsResponse(BaseModel):
    """Schema response untuk analytics voucher"""
    id: int
    voucher_id: int
    voucher_code: str
    voucher_type: Optional[str]
    date: datetime
    usage_count: int
    total_discount: Decimal
    total_revenue_impact: Decimal
    redemption_rate: Decimal
    avg_discount_per_use: Decimal
    
    class Config:
        from_attributes = True

class DashboardMetricsResponse(BaseModel):
    """Schema response untuk metrics dashboard"""
    id: int
    metric_name: str
    metric_type: str
    date: datetime
    value: Decimal
    previous_value: Optional[Decimal]
    percentage_change: Optional[Decimal]
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    """Schema untuk summary dashboard"""
    total_revenue: Decimal
    total_transactions: int
    total_users: int
    total_products: int
    revenue_growth: Optional[Decimal]
    transaction_growth: Optional[Decimal]
    user_growth: Optional[Decimal]
    top_products: List[Dict[str, Any]]
    top_vouchers: List[Dict[str, Any]]

class AnalyticsFilter(BaseModel):
    """Schema untuk filter analytics"""
    start_date: Optional[datetime] = Field(None, description="Tanggal mulai filter")
    end_date: Optional[datetime] = Field(None, description="Tanggal akhir filter")
    event_type: Optional[str] = Field(None, description="Filter berdasarkan tipe event")
    user_id: Optional[int] = Field(None, description="Filter berdasarkan user ID")
    product_id: Optional[int] = Field(None, description="Filter berdasarkan product ID")
    voucher_id: Optional[int] = Field(None, description="Filter berdasarkan voucher ID")
    category: Optional[str] = Field(None, description="Filter berdasarkan kategori")

class ChartDataPoint(BaseModel):
    """Schema untuk data point chart"""
    label: str
    value: Decimal
    date: Optional[datetime] = None

class ChartData(BaseModel):
    """Schema untuk data chart"""
    title: str
    chart_type: str  # line, bar, pie, etc.
    data_points: List[ChartDataPoint]
    labels: List[str]
    datasets: List[Dict[str, Any]]

class AnalyticsReport(BaseModel):
    """Schema untuk laporan analytics"""
    report_type: str
    period: str
    generated_at: datetime
    summary: DashboardSummary
    charts: List[ChartData]
    raw_data: Optional[List[Dict[str, Any]]] = None
