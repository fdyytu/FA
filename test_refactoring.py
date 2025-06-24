"""
Script untuk testing refactoring yang telah dilakukan
Memastikan semua import dan logging berfungsi dengan baik
"""

import sys
import os

# Add the workspace to Python path
sys.path.append('/home/user/workspace')

def test_logging_system():
    """Test sistem logging baru"""
    print("=== Testing Logging System ===")
    try:
        from app.common.logging.admin_logger import admin_logger
        
        # Test basic logging
        admin_logger.info("Test info message")
        admin_logger.warning("Test warning message")
        admin_logger.error("Test error message", Exception("Test exception"))
        
        # Test logging with extra data
        admin_logger.info("Test with extra data", {"user_id": "123", "action": "login"})
        
        print("✅ Logging system test passed")
        return True
    except Exception as e:
        print(f"❌ Logging system test failed: {e}")
        return False

def test_repository_imports():
    """Test import semua repository yang sudah dipecah"""
    print("\n=== Testing Repository Imports ===")
    try:
        from app.domains.admin.repositories import (
            AdminRepository,
            AdminConfigRepository,
            PPOBMarginRepository,
            UserManagementRepository,
            ProductManagementRepository,
            DashboardRepository,
            AuditLogRepository
        )
        
        print("✅ All repository imports successful")
        return True
    except Exception as e:
        print(f"❌ Repository imports failed: {e}")
        return False

def test_controller_imports():
    """Test import controller Discord yang sudah dipecah"""
    print("\n=== Testing Controller Imports ===")
    try:
        from app.domains.admin.controllers.discord import (
            discord_stats_controller,
            discord_bots_controller,
            discord_worlds_controller
        )
        
        from app.domains.admin.controllers.admin_discord_controller import admin_discord_controller
        
        print("✅ All controller imports successful")
        return True
    except Exception as e:
        print(f"❌ Controller imports failed: {e}")
        return False

def test_schema_imports():
    """Test import schema yang sudah dipecah"""
    print("\n=== Testing Schema Imports ===")
    try:
        from app.domains.admin.schemas.admin_schemas import (
            AdminRole,
            AdminCreate,
            AdminResponse,
            UserManagementResponse,
            ProductCreate,
            DashboardStats,
            PaginationParams,
            DiscordConfigCreate
        )
        
        print("✅ All schema imports successful")
        return True
    except Exception as e:
        print(f"❌ Schema imports failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility"""
    print("\n=== Testing Backward Compatibility ===")
    try:
        # Test old import style still works
        from app.domains.admin.repositories.admin_basic_repository import AdminRepository
        from app.domains.admin.schemas.admin_schemas import AdminCreate
        
        print("✅ Backward compatibility test passed")
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Refactoring Tests\n")
    
    tests = [
        test_logging_system,
        test_repository_imports,
        test_controller_imports,
        test_schema_imports,
        test_backward_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring successful!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
