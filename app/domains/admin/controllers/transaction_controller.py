"""
Transaction Controller - Refactored
Menggunakan composition pattern dengan controller-controller kecil
File ini sebagai facade untuk backward compatibility
"""

from fastapi import APIRouter
import logging

from .transaction.transaction_main_controller import TransactionMainController
from .transaction.transaction_stats_controller import TransactionStatsController
from .transaction.transaction_management_controller import TransactionManagementController

logger = logging.getLogger(__name__)


class TransactionController:
    """
    Transaction Controller - Facade pattern
    Menggabungkan semua controller transaction kecil
    Menyediakan interface yang sama untuk backward compatibility
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_controllers()
    
    def _setup_controllers(self):
        """Setup dan gabungkan semua controller transaction"""
        try:
            # Initialize sub-controllers
            main_controller = TransactionMainController()
            stats_controller = TransactionStatsController()
            management_controller = TransactionManagementController()
            
            # Include all routers
            self.router.include_router(main_controller.router, tags=["transaction-main"])
            self.router.include_router(stats_controller.router, tags=["transaction-stats"])
            self.router.include_router(management_controller.router, tags=["transaction-management"])
            
            logger.info("Transaction controllers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing transaction controllers: {str(e)}", exc_info=True)
            raise


# Initialize controller instance
transaction_controller = TransactionController()
