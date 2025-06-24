"""
Admin Repositories Package
Package yang berisi semua repository classes yang telah dipecah
"""

# Import semua repositories dari modul terpisah
from .admin_basic_repository import AdminRepository
from .admin_config_repository import AdminConfigRepository
from .ppob_margin_repository import PPOBMarginRepository
from .user_management_repository import UserManagementRepository
from .product_management_repository import ProductManagementRepository
from .dashboard_repository import DashboardRepository
from .dashboard_stats_repository import DashboardStatsRepository
from .dashboard_transactions_repository import DashboardTransactionsRepository
from .dashboard_products_repository import DashboardProductsRepository
from .audit_log_repository import AuditLogRepository

# Export semua untuk backward compatibility
__all__ = [
    'AdminRepository',
    'AdminConfigRepository',
    'PPOBMarginRepository',
    'UserManagementRepository',
    'ProductManagementRepository',
    'DashboardRepository',
    'DashboardStatsRepository',
    'DashboardTransactionsRepository',
    'DashboardProductsRepository',
    'AuditLogRepository'
]
