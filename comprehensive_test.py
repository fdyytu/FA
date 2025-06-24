"""
Comprehensive test untuk memastikan refactoring tidak merusak functionality
"""

import sys
import os
import traceback

# Add the workspace to Python path
sys.path.append('/home/user/workspace')

def test_logging_functionality():
    """Test logging functionality secara detail"""
    print("=== Testing Logging Functionality ===")
    try:
        from app.common.logging.admin_logger import admin_logger
        
        # Test all logging levels
        admin_logger.debug("Debug message test")
        admin_logger.info("Info message test")
        admin_logger.warning("Warning message test")
        admin_logger.error("Error message test", Exception("Test exception"))
        
        # Test with extra data
        admin_logger.info("Test with complex data", {
            "user_id": "123",
            "action": "login",
            "metadata": {"ip": "192.168.1.1", "browser": "Chrome"}
        })
        
        print("✅ Logging functionality test passed")
        return True
    except Exception as e:
        print(f"❌ Logging functionality test failed: {e}")
        print(traceback.format_exc())
        return False

def test_repository_structure():
    """Test struktur repository yang sudah dipecah"""
    print("\n=== Testing Repository Structure ===")
    
    # Test individual repository files exist
    repository_files = [
        'app/domains/admin/repositories/admin_basic_repository.py',
        'app/domains/admin/repositories/admin_config_repository.py',
        'app/domains/admin/repositories/ppob_margin_repository.py',
        'app/domains/admin/repositories/user_management_repository.py',
        'app/domains/admin/repositories/product_management_repository.py',
        'app/domains/admin/repositories/dashboard_stats_repository.py',
        'app/domains/admin/repositories/dashboard_transactions_repository.py',
        'app/domains/admin/repositories/dashboard_products_repository.py',
        'app/domains/admin/repositories/dashboard_repository.py',
        'app/domains/admin/repositories/audit_log_repository.py'
    ]
    
    missing_files = []
    for file_path in repository_files:
        full_path = f'/home/user/workspace/{file_path}'
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing repository files: {missing_files}")
        return False
    
    print("✅ All repository files exist")
    
    # Test that old admin_repository.py is removed
    old_file = '/home/user/workspace/app/domains/admin/repositories/admin_repository.py'
    if os.path.exists(old_file):
        print("❌ Old admin_repository.py still exists")
        return False
    
    print("✅ Old admin_repository.py properly removed")
    return True

def test_controller_structure():
    """Test struktur controller yang sudah dipecah"""
    print("\n=== Testing Controller Structure ===")
    
    # Test Discord controller files exist
    discord_files = [
        'app/domains/admin/controllers/discord/__init__.py',
        'app/domains/admin/controllers/discord/discord_stats_controller.py',
        'app/domains/admin/controllers/discord/discord_bots_controller.py',
        'app/domains/admin/controllers/discord/discord_worlds_controller.py'
    ]
    
    missing_files = []
    for file_path in discord_files:
        full_path = f'/home/user/workspace/{file_path}'
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing Discord controller files: {missing_files}")
        return False
    
    print("✅ All Discord controller files exist")
    
    # Test main controller file exists and is updated
    main_controller = '/home/user/workspace/app/domains/admin/controllers/admin_discord_controller.py'
    if not os.path.exists(main_controller):
        print("❌ Main Discord controller missing")
        return False
    
    print("✅ Main Discord controller exists")
    return True

def test_schema_structure():
    """Test struktur schema yang sudah dipecah"""
    print("\n=== Testing Schema Structure ===")
    
    # Test schema component files exist
    schema_files = [
        'app/domains/admin/schemas/components/__init__.py',
        'app/domains/admin/schemas/components/admin_schemas.py',
        'app/domains/admin/schemas/components/user_management_schemas.py',
        'app/domains/admin/schemas/components/product_management_schemas.py',
        'app/domains/admin/schemas/components/configuration_schemas.py',
        'app/domains/admin/schemas/components/dashboard_schemas.py',
        'app/domains/admin/schemas/components/common_schemas.py',
        'app/domains/admin/schemas/components/discord_schemas.py'
    ]
    
    missing_files = []
    for file_path in schema_files:
        full_path = f'/home/user/workspace/{file_path}'
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing schema component files: {missing_files}")
        return False
    
    print("✅ All schema component files exist")
    
    # Test main schema file exists and is updated
    main_schema = '/home/user/workspace/app/domains/admin/schemas/admin_schemas.py'
    if not os.path.exists(main_schema):
        print("❌ Main schema file missing")
        return False
    
    print("✅ Main schema file exists")
    return True

def test_file_content_quality():
    """Test kualitas konten file yang sudah dipecah"""
    print("\n=== Testing File Content Quality ===")
    
    # Test repository files have proper class definitions
    try:
        # Check admin_basic_repository
        with open('/home/user/workspace/app/domains/admin/repositories/admin_basic_repository.py', 'r') as f:
            content = f.read()
            if 'class AdminRepository' not in content:
                print("❌ AdminRepository class not found in admin_basic_repository.py")
                return False
            if 'admin_logger' not in content:
                print("❌ admin_logger not used in admin_basic_repository.py")
                return False
        
        # Check dashboard_repository uses composition
        with open('/home/user/workspace/app/domains/admin/repositories/dashboard_repository.py', 'r') as f:
            content = f.read()
            if 'DashboardStatsRepository' not in content:
                print("❌ Composition pattern not implemented in dashboard_repository.py")
                return False
        
        print("✅ File content quality check passed")
        return True
        
    except Exception as e:
        print(f"❌ File content quality check failed: {e}")
        return False

def test_documentation_exists():
    """Test dokumentasi ada dan lengkap"""
    print("\n=== Testing Documentation ===")
    
    doc_file = '/home/user/workspace/REFACTORING_DOCUMENTATION.md'
    if not os.path.exists(doc_file):
        print("❌ Documentation file missing")
        return False
    
    try:
        with open(doc_file, 'r') as f:
            content = f.read()
            required_sections = [
                '## Overview',
                '### 1. Sistem Logging Baru',
                '### 2. Pemecahan Repository Besar',
                '### 3. Pemecahan Controller Besar',
                '### 4. Pemecahan Schemas Besar',
                '## SOLID Principles yang Diterapkan'
            ]
            
            for section in required_sections:
                if section not in content:
                    print(f"❌ Missing documentation section: {section}")
                    return False
        
        print("✅ Documentation is complete")
        return True
        
    except Exception as e:
        print(f"❌ Documentation check failed: {e}")
        return False

def main():
    """Run comprehensive tests"""
    print("🚀 Starting Comprehensive Refactoring Tests\n")
    
    tests = [
        test_logging_functionality,
        test_repository_structure,
        test_controller_structure,
        test_schema_structure,
        test_file_content_quality,
        test_documentation_exists
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Comprehensive Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All comprehensive tests passed! Refactoring is solid!")
        return True
    else:
        print("⚠️  Some tests failed. Refactoring needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
