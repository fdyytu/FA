from fastapi import APIRouter
import logging
import time

from .admin import AdminCrudController, AdminAuthController, AdminAuditController

# Setup enhanced logging
logger = logging.getLogger(__name__)


class AdminManagementController:
    """
    Facade Controller untuk manajemen admin
    
    Pattern: Facade Pattern - Menyediakan interface sederhana untuk sub-controllers
    Single Responsibility: Orchestrate admin management operations
    
    Sub-controllers:
    - AdminCrudController: Handle CRUD operations
    - AdminAuthController: Handle authentication & authorization  
    - AdminAuditController: Handle audit logs & monitoring
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._initialize_controllers()
        self._setup_routes()
        logger.info("AdminManagementController (Facade) initialized with enhanced logging")
    
    def _initialize_controllers(self):
        """Initialize sub-controllers dengan logging"""
        start_time = time.time()
        
        try:
            logger.debug("Initializing AdminManagementController sub-controllers...")
            
            # Initialize sub-controllers
            self.crud_controller = AdminCrudController()
            self.auth_controller = AdminAuthController()
            self.audit_controller = AdminAuditController()
            
            duration = time.time() - start_time
            logger.info(f"Successfully initialized all admin sub-controllers in {duration:.3f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error initializing admin sub-controllers after {duration:.3f}s: {str(e)}", exc_info=True)
            raise
    
    def _setup_routes(self):
        """Setup routes dengan delegation ke sub-controllers"""
        start_time = time.time()
        
        try:
            logger.debug("Setting up AdminManagementController routes...")
            
            # Include CRUD routes (admin management)
            self.router.include_router(
                self.crud_controller.router,
                tags=["Admin CRUD"],
                prefix=""
            )
            
            # Include Auth routes (permissions, profile, validation)
            self.router.include_router(
                self.auth_controller.router,
                tags=["Admin Auth"],
                prefix=""
            )
            
            # Include Audit routes (audit logs, monitoring)
            self.router.include_router(
                self.audit_controller.router,
                tags=["Admin Audit"],
                prefix=""
            )
            
            duration = time.time() - start_time
            logger.info(f"Successfully setup admin management routes in {duration:.3f}s")
            logger.info("Admin Management Facade Pattern implemented with 3 sub-controllers")
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error setting up admin routes after {duration:.3f}s: {str(e)}", exc_info=True)
            raise


# Initialize facade controller
admin_management_controller = AdminManagementController()
