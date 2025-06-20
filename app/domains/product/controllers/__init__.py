"""
Product controllers yang telah dipecah menjadi beberapa file terpisah
untuk meningkatkan maintainability dan mengikuti prinsip Single Responsibility.
"""

from .product_crud_controller import ProductCRUDController
from .product_search_controller import ProductSearchController
from .product_stats_controller import ProductStatsController

__all__ = [
    'ProductCRUDController',
    'ProductSearchController',
    'ProductStatsController'
]

# Dokumentasi untuk setiap controller:

# ProductCRUDController
# - Mengelola operasi Create, Read, Update, Delete produk
# - Endpoint dasar untuk manajemen produk

# ProductSearchController  
# - Mengelola operasi pencarian dan filter produk
# - Endpoint untuk search, filter by category, provider, price range

# ProductStatsController
# - Mengelola statistik dan analytics produk
# - Endpoint untuk dashboard dan reporting
