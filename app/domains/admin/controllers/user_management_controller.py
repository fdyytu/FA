from fastapi import APIRouter
import logging

from .user import (
    user_crud_controller,
    user_stats_controller,
    user_validation_controller
)

logger = logging.getLogger(__name__)


class UserManagementController:
    """
    Facade Controller untuk manajemen user - Facade Pattern: Menggabungkan semua user controllers
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes dengan menggabungkan semua sub-controllers"""
        # Include CRUD operations
        self.router.include_router(
            user_crud_controller.router,
            tags=["User Management - CRUD"]
        )
        
        # Include stats operations  
        self.router.include_router(
            user_stats_controller.router,
            tags=["User Management - Stats"]
        )
        
        # Include validation operations
        self.router.include_router(
            user_validation_controller.router,
            tags=["User Management - Validation"]
        )


# Initialize controller
user_management_controller = UserManagementController()
