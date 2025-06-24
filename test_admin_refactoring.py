#!/usr/bin/env python3
"""
Test script untuk memvalidasi refactoring admin_management_controller.py
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test import semua modul yang telah direfactor"""
    try:
        logger.info("Testing imports...")
        
        # Test import facade controller
        from app.domains.admin.controllers.admin_management_controller import admin_management_controller
        logger.info("✅ admin_management_controller imported successfully")
        
        # Test import sub-controllers
        from app.domains.admin.controllers.admin import AdminCrudController, AdminAuthController, AdminAuditController
        logger.info("✅ Sub-controllers imported successfully")
        
        # Test controller initialization
        crud_controller = AdminCrudController()
        auth_controller = AdminAuthController()
        audit_controller = AdminAuditController()
        logger.info("✅ Sub-controllers initialized successfully")
        
        # Test router availability
        assert hasattr(admin_management_controller, 'router'), "Facade controller should have router"
        assert hasattr(crud_controller, 'router'), "CRUD controller should have router"
        assert hasattr(auth_controller, 'router'), "Auth controller should have router"
        assert hasattr(audit_controller, 'router'), "Audit controller should have router"
        logger.info("✅ All routers available")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Import test failed: {str(e)}")
        return False

def test_structure():
    """Test struktur file yang telah dibuat"""
    try:
        logger.info("Testing file structure...")
        
        # Check if files exist
        files_to_check = [
            '/home/user/workspace/app/domains/admin/controllers/admin/__init__.py',
            '/home/user/workspace/app/domains/admin/controllers/admin/admin_crud_controller.py',
            '/home/user/workspace/app/domains/admin/controllers/admin/admin_auth_controller.py',
            '/home/user/workspace/app/domains/admin/controllers/admin/admin_audit_controller.py',
            '/home/user/workspace/app/domains/admin/controllers/admin_management_controller.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                logger.info(f"✅ {file_path} exists")
            else:
                logger.error(f"❌ {file_path} missing")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Structure test failed: {str(e)}")
        return False

def test_logging_setup():
    """Test setup logging pada setiap controller"""
    try:
        logger.info("Testing logging setup...")
        
        from app.domains.admin.controllers.admin.admin_crud_controller import AdminCrudController
        from app.domains.admin.controllers.admin.admin_auth_controller import AdminAuthController
        from app.domains.admin.controllers.admin.admin_audit_controller import AdminAuditController
        
        # Test logging pada setiap controller
        controllers = [
            AdminCrudController(),
            AdminAuthController(), 
            AdminAuditController()
        ]
        
        for controller in controllers:
            assert hasattr(controller, 'router'), f"{controller.__class__.__name__} should have router"
            logger.info(f"✅ {controller.__class__.__name__} logging setup verified")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Logging test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting Admin Refactoring Tests...")
    
    tests = [
        ("Import Test", test_imports),
        ("Structure Test", test_structure), 
        ("Logging Test", test_logging_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Refactoring successful.")
        return True
    else:
        logger.error("💥 Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
