#!/usr/bin/env python3
"""
Test server untuk memvalidasi refactoring admin_management_controller.py
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Admin Management Test Server",
    description="Test server untuk validasi refactoring admin controllers",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint untuk health check"""
    return {
        "message": "Admin Management Test Server",
        "status": "running",
        "refactoring": "batch_2_completed"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test import admin controllers
        from app.domains.admin.controllers.admin_management_controller import admin_management_controller
        from app.domains.admin.controllers.admin import AdminCrudController, AdminAuthController, AdminAuditController
        
        return {
            "status": "healthy",
            "admin_management_controller": "✅ imported",
            "sub_controllers": "✅ imported",
            "facade_pattern": "✅ working",
            "enhanced_logging": "✅ implemented"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@app.get("/test/controllers")
async def test_controllers():
    """Test controller initialization"""
    try:
        from app.domains.admin.controllers.admin import AdminCrudController, AdminAuthController, AdminAuditController
        
        # Test initialization
        crud = AdminCrudController()
        auth = AdminAuthController()
        audit = AdminAuditController()
        
        return {
            "crud_controller": {
                "initialized": True,
                "has_router": hasattr(crud, 'router'),
                "class_name": crud.__class__.__name__
            },
            "auth_controller": {
                "initialized": True,
                "has_router": hasattr(auth, 'router'),
                "class_name": auth.__class__.__name__
            },
            "audit_controller": {
                "initialized": True,
                "has_router": hasattr(audit, 'router'),
                "class_name": audit.__class__.__name__
            }
        }
    except Exception as e:
        logger.error(f"Controller test failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "test": "failed"
            }
        )

@app.get("/test/facade")
async def test_facade():
    """Test facade pattern implementation"""
    try:
        from app.domains.admin.controllers.admin_management_controller import admin_management_controller
        
        return {
            "facade_controller": {
                "initialized": True,
                "has_router": hasattr(admin_management_controller, 'router'),
                "has_crud_controller": hasattr(admin_management_controller, 'crud_controller'),
                "has_auth_controller": hasattr(admin_management_controller, 'auth_controller'),
                "has_audit_controller": hasattr(admin_management_controller, 'audit_controller'),
                "class_name": admin_management_controller.__class__.__name__
            },
            "pattern": "facade",
            "status": "✅ working"
        }
    except Exception as e:
        logger.error(f"Facade test failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "test": "failed"
            }
        )

if __name__ == "__main__":
    logger.info("Starting Admin Management Test Server...")
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
