"""
Product controllers package
Memecah product management controller menjadi modul-modul kecil
"""

from .product_crud_controller import ProductCrudController
from .product_write_controller import ProductWriteController
from .product_stats_controller import ProductStatsController
from .product_management_controller import ProductManagementController

__all__ = [
    'ProductCrudController',
    'ProductWriteController',
    'ProductStatsController',
    'ProductManagementController'
]
