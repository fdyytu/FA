"""
Admin Repository Module

Modul ini mengexport semua repository classes untuk digunakan
oleh service layer. File ini dibuat untuk menjaga backward compatibility
dengan import yang sudah ada di service layer.
"""

from .admin_basic_repository import AdminRepository
from .audit_log_repository import AuditLogRepository
from .admin_config_repository import AdminConfigRepository
from .ppob_margin_repository import PPOBMarginRepository
from .product_management_repository import ProductManagementRepository
from .user_management_repository import UserManagementRepository
from .dashboard_repository import DashboardRepository
from .dashboard_stats_repository import DashboardStatsRepository
from .dashboard_products_repository import DashboardProductsRepository
from .dashboard_transactions_repository import DashboardTransactionsRepository

__all__ = [
    'AdminRepository',
    'AuditLogRepository',
    'AdminConfigRepository',
    'PPOBMarginRepository',
    'ProductManagementRepository',
    'UserManagementRepository',
    'DashboardRepository',
    'DashboardStatsRepository',
    'DashboardProductsRepository',
    'DashboardTransactionsRepository'
]
