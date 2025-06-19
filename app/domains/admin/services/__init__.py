"""
Modul ini berisi implementasi service untuk Admin.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.admin.services.admin_management_service import AdminManagementService
from app.domains.admin.services.configuration_service import ConfigurationService
from app.domains.admin.services.margin_management_service import MarginManagementService
from app.domains.admin.services.user_management_service import UserManagementService
from app.domains.admin.services.product_management_service import ProductManagementService
from app.domains.admin.services.dashboard_service import DashboardService

__all__ = [
    'AdminManagementService',
    'ConfigurationService',
    'MarginManagementService',
    'UserManagementService',
    'ProductManagementService',
    'DashboardService'
]

# Dokumentasi tambahan untuk setiap service:

# AdminManagementService
# - Menangani operasi CRUD untuk admin
# - Mencatat audit log untuk setiap perubahan

# ConfigurationService
# - Mengelola konfigurasi sistem
# - Menyimpan dan memperbarui pengaturan aplikasi

# MarginManagementService
# - Mengelola konfigurasi margin untuk produk PPOB
# - Menghitung harga dengan margin

# UserManagementService
# - Mengelola data pengguna oleh admin
# - Menyediakan statistik pengguna

# ProductManagementService
# - Mengelola produk PPOB
# - Menangani kategori dan harga produk

# DashboardService
# - Menyediakan data untuk dashboard admin
# - Mengagregasi statistik dan metrics
