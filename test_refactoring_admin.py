#!/usr/bin/env python3
"""
Test script untuk memastikan refactoring tidak merusak import dan struktur
"""

import sys
import os

# Add the workspace to Python path
sys.path.insert(0, '/home/user/workspace')

def test_user_controller_imports():
    """Test import user controllers"""
    try:
        from app.domains.admin.controllers.user_management_controller import user_management_controller
        from app.domains.admin.controllers.user import (
            user_crud_controller,
            user_stats_controller,
            user_validation_controller
        )
        print("✅ User controller imports berhasil")
        return True
    except Exception as e:
        print(f"❌ User controller imports gagal: {e}")
        return False

def test_product_service_imports():
    """Test import product services"""
    try:
        from app.domains.admin.services.product_management_service import ProductManagementService
        from app.domains.admin.services.product import (
            ProductCrudService,
            ProductValidationService,
            ProductStatsService
        )
        print("✅ Product service imports berhasil")
        return True
    except Exception as e:
        print(f"❌ Product service imports gagal: {e}")
        return False

def test_structure_integrity():
    """Test struktur file yang dibuat"""
    files_to_check = [
        '/home/user/workspace/app/domains/admin/controllers/user/__init__.py',
        '/home/user/workspace/app/domains/admin/controllers/user/user_crud_controller.py',
        '/home/user/workspace/app/domains/admin/controllers/user/user_stats_controller.py',
        '/home/user/workspace/app/domains/admin/controllers/user/user_validation_controller.py',
        '/home/user/workspace/app/domains/admin/services/product/__init__.py',
        '/home/user/workspace/app/domains/admin/services/product/product_crud_service.py',
        '/home/user/workspace/app/domains/admin/services/product/product_validation_service.py',
        '/home/user/workspace/app/domains/admin/services/product/product_stats_service.py',
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} ada")
        else:
            print(f"❌ {file_path} tidak ada")
            all_exist = False
    
    return all_exist

def main():
    """Main test function"""
    print("🧪 Memulai testing refactoring...")
    print("=" * 50)
    
    tests = [
        test_structure_integrity,
        test_user_controller_imports,
        test_product_service_imports,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Hasil Testing: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Semua tests berhasil! Refactoring aman.")
        return True
    else:
        print("⚠️  Ada tests yang gagal. Perlu perbaikan.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
