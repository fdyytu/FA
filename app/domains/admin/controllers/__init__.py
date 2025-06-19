"""
Admin Controllers Module

Berisi semua controller untuk admin panel yang telah dipecah berdasarkan Single Responsibility Principle:
- AuthController: Autentikasi admin
- AdminManagementController: Manajemen admin
- ConfigurationController: Konfigurasi sistem
- UserManagementController: Manajemen user
- ProductManagementController: Manajemen produk
- DashboardController: Dashboard dan statistik
- TransactionController: Manajemen transaksi
"""

from .auth_controller import auth_controller
from .admin_management_controller import admin_management_controller
from .configuration_controller import configuration_controller
from .user_management_controller import user_management_controller
from .product_management_controller import product_management_controller
from .dashboard_controller import dashboard_controller
from .transaction_controller import transaction_controller

__all__ = [
    "auth_controller",
    "admin_management_controller", 
    "configuration_controller",
    "user_management_controller",
    "product_management_controller",
    "dashboard_controller",
    "transaction_controller"
]
