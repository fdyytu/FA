"""
Dashboard schemas - dipecah dari admin_schemas.py
Berisi schema untuk dashboard data
"""

from pydantic import BaseModel
from typing import List, Dict, Any


class DashboardStats(BaseModel):
    """Schema untuk statistik dashboard"""
    total_users: int
    active_users: int
    total_transactions: int
    total_revenue: float
    pending_transactions: int
    failed_transactions: int


class TransactionStats(BaseModel):
    """Schema untuk statistik transaksi"""
    date: str
    count: int
    amount: float


class DashboardResponse(BaseModel):
    """Schema response dashboard"""
    stats: DashboardStats
    recent_transactions: List[Dict[str, Any]]
    transaction_trends: List[TransactionStats]
    top_products: List[Dict[str, Any]]
