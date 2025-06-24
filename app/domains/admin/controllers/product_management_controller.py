"""
Product Management Controller - Refactored
Menggunakan composition pattern dengan controller-controller kecil
File ini sebagai facade untuk backward compatibility
"""

from fastapi import APIRouter
import logging

from .product.product_crud_controller import ProductCrudController
from .product.product_write_controller import ProductWriteController
from .product.product_stats_controller import ProductStatsController
from .product.product_management_controller import ProductManagementController as ProductStatusController

logger = logging.getLogger(__name__)


class ProductManagementController:
    """
    Product Management Controller - Facade pattern
    Menggabungkan semua controller product kecil
    Menyediakan interface yang sama untuk backward compatibility
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_controllers()
    
    def _setup_controllers(self):
        """Setup dan gabungkan semua controller product"""
        try:
            # Initialize sub-controllers
            crud_controller = ProductCrudController()
            write_controller = ProductWriteController()
            stats_controller = ProductStatsController()
            status_controller = ProductStatusController()
            
            # Include all routers
            self.router.include_router(crud_controller.router, tags=["product-crud"])
            self.router.include_router(write_controller.router, tags=["product-write"])
            self.router.include_router(stats_controller.router, tags=["product-stats"])
            self.router.include_router(status_controller.router, tags=["product-status"])
            
            logger.info("Product management controllers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing product management controllers: {str(e)}", exc_info=True)
            raise


# Initialize controller for backward compatibility
product_management_controller = ProductManagementController()
