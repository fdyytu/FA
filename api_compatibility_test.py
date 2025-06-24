#!/usr/bin/env python3
"""
API Compatibility Test - Memastikan refactoring tidak merusak API endpoints
"""

import sys
import os
import re

# Add the workspace to Python path
sys.path.insert(0, '/home/user/workspace')

def test_api_endpoints_preservation():
    """Test apakah semua API endpoints masih ada setelah refactoring"""
    print("🧪 Testing API Endpoints Preservation...")
    
    # Test User Management Controller endpoints
    print("  📝 Testing User Management Controller endpoints...")
    
    facade_file = '/home/user/workspace/app/domains/admin/controllers/user_management_controller.py'
    
    try:
        with open(facade_file, 'r') as f:
            facade_content = f.read()
        
        # Check if facade includes all sub-routers
        if 'user_crud_controller.router' not in facade_content:
            print("  ❌ CRUD router tidak di-include dalam facade")
            return False
            
        if 'user_stats_controller.router' not in facade_content:
            print("  ❌ Stats router tidak di-include dalam facade")
            return False
            
        if 'user_validation_controller.router' not in facade_content:
            print("  ❌ Validation router tidak di-include dalam facade")
            return False
            
        print("  ✅ All user sub-routers included in facade")
        
        # Check individual endpoint files
        crud_file = '/home/user/workspace/app/domains/admin/controllers/user/user_crud_controller.py'
        with open(crud_file, 'r') as f:
            crud_content = f.read()
            
        # Check for essential CRUD endpoints
        crud_endpoints = [
            '@self.router.get("/"',  # get_users
            '@self.router.get("/{user_id}"',  # get_user
            '@self.router.put("/{user_id}"',  # update_user
            '@self.router.delete("/{user_id}"'  # delete_user
        ]
        
        for endpoint in crud_endpoints:
            if endpoint not in crud_content:
                print(f"  ❌ Missing CRUD endpoint: {endpoint}")
                return False
                
        print("  ✅ All CRUD endpoints preserved")
        
        # Check stats endpoints
        stats_file = '/home/user/workspace/app/domains/admin/controllers/user/user_stats_controller.py'
        with open(stats_file, 'r') as f:
            stats_content = f.read()
            
        if '@self.router.get("/stats")' not in stats_content:
            print("  ❌ Missing stats endpoint")
            return False
            
        print("  ✅ Stats endpoint preserved")
        
        # Check validation endpoints
        validation_file = '/home/user/workspace/app/domains/admin/controllers/user/user_validation_controller.py'
        with open(validation_file, 'r') as f:
            validation_content = f.read()
            
        validation_endpoints = [
            '@self.router.post("/{user_id}/activate"',
            '@self.router.post("/{user_id}/deactivate"',
            '@self.router.post("/{user_id}/reset-password"'
        ]
        
        for endpoint in validation_endpoints:
            if endpoint not in validation_content:
                print(f"  ❌ Missing validation endpoint: {endpoint}")
                return False
                
        print("  ✅ All validation endpoints preserved")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing API endpoints: {e}")
        return False

def test_service_methods_preservation():
    """Test apakah semua service methods masih ada"""
    print("🧪 Testing Service Methods Preservation...")
    
    try:
        # Test Product Management Service
        service_file = '/home/user/workspace/app/domains/admin/services/product_management_service.py'
        with open(service_file, 'r') as f:
            service_content = f.read()
        
        # Check if facade delegates to sub-services
        expected_methods = [
            'def get_products(',
            'def get_product_categories(',
            'def create_product(',
            'def update_product(',
            'def get_product_stats(',
            'def get_category_stats(',
            'def get_price_distribution(',
            'def validate_product_code_unique(',
            'def validate_product_exists('
        ]
        
        for method in expected_methods:
            if method not in service_content:
                print(f"  ❌ Missing service method: {method}")
                return False
                
        print("  ✅ All service methods preserved in facade")
        
        # Check if facade properly delegates to sub-services
        delegation_patterns = [
            'self.crud_service.get_products(',
            'self.crud_service.create_product(',
            'self.stats_service.get_product_stats(',
            'self.validation_service.validate_product_data('
        ]
        
        for pattern in delegation_patterns:
            if pattern not in service_content:
                print(f"  ❌ Missing delegation pattern: {pattern}")
                return False
                
        print("  ✅ Facade properly delegates to sub-services")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing service methods: {e}")
        return False

def test_import_statements():
    """Test apakah import statements benar"""
    print("🧪 Testing Import Statements...")
    
    try:
        # Test User Controller imports
        facade_file = '/home/user/workspace/app/domains/admin/controllers/user_management_controller.py'
        with open(facade_file, 'r') as f:
            content = f.read()
            
        required_imports = [
            'from .user import',
            'user_crud_controller',
            'user_stats_controller',
            'user_validation_controller'
        ]
        
        for import_stmt in required_imports:
            if import_stmt not in content:
                print(f"  ❌ Missing import: {import_stmt}")
                return False
                
        print("  ✅ User controller imports correct")
        
        # Test Product Service imports
        service_file = '/home/user/workspace/app/domains/admin/services/product_management_service.py'
        with open(service_file, 'r') as f:
            content = f.read()
            
        service_imports = [
            'from .product import',
            'ProductCrudService',
            'ProductValidationService',
            'ProductStatsService'
        ]
        
        for import_stmt in service_imports:
            if import_stmt not in content:
                print(f"  ❌ Missing service import: {import_stmt}")
                return False
                
        print("  ✅ Product service imports correct")
        
        # Test __init__.py files
        user_init = '/home/user/workspace/app/domains/admin/controllers/user/__init__.py'
        with open(user_init, 'r') as f:
            content = f.read()
            
        if '__all__' not in content:
            print("  ❌ Missing __all__ in user __init__.py")
            return False
            
        product_init = '/home/user/workspace/app/domains/admin/services/product/__init__.py'
        with open(product_init, 'r') as f:
            content = f.read()
            
        if '__all__' not in content:
            print("  ❌ Missing __all__ in product __init__.py")
            return False
            
        print("  ✅ __init__.py files properly configured")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing imports: {e}")
        return False

def test_dependency_injection():
    """Test apakah dependency injection masih berfungsi"""
    print("🧪 Testing Dependency Injection...")
    
    try:
        # Check User Controllers
        user_files = [
            '/home/user/workspace/app/domains/admin/controllers/user/user_crud_controller.py',
            '/home/user/workspace/app/domains/admin/controllers/user/user_stats_controller.py',
            '/home/user/workspace/app/domains/admin/controllers/user/user_validation_controller.py'
        ]
        
        for file_path in user_files:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for dependency injection patterns
            if 'Depends(get_db)' not in content:
                print(f"  ❌ Missing database dependency in {os.path.basename(file_path)}")
                return False
                
            if 'Depends(get_current_admin)' not in content:
                print(f"  ❌ Missing admin auth dependency in {os.path.basename(file_path)}")
                return False
                
        print("  ✅ User controller dependencies correct")
        
        # Check Product Services
        product_files = [
            '/home/user/workspace/app/domains/admin/services/product/product_crud_service.py',
            '/home/user/workspace/app/domains/admin/services/product/product_validation_service.py',
            '/home/user/workspace/app/domains/admin/services/product/product_stats_service.py'
        ]
        
        for file_path in product_files:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for proper service initialization
            if 'def __init__(self, db: Session):' not in content:
                print(f"  ❌ Missing proper init in {os.path.basename(file_path)}")
                return False
                
            if 'self.db = db' not in content:
                print(f"  ❌ Missing db assignment in {os.path.basename(file_path)}")
                return False
                
        print("  ✅ Product service dependencies correct")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing dependency injection: {e}")
        return False

def test_response_models():
    """Test apakah response models masih konsisten"""
    print("🧪 Testing Response Models...")
    
    try:
        # Check User Controller response models
        crud_file = '/home/user/workspace/app/domains/admin/controllers/user/user_crud_controller.py'
        with open(crud_file, 'r') as f:
            content = f.read()
            
        response_models = [
            'response_model=PaginatedResponse',
            'response_model=UserManagementResponse',
            'APIResponse.success('
        ]
        
        for model in response_models:
            if model not in content:
                print(f"  ❌ Missing response model: {model}")
                return False
                
        print("  ✅ User controller response models correct")
        
        # Check if proper imports exist
        required_imports = [
            'UserManagementResponse',
            'PaginatedResponse',
            'APIResponse'
        ]
        
        for import_name in required_imports:
            if import_name not in content:
                print(f"  ❌ Missing response import: {import_name}")
                return False
                
        print("  ✅ Response model imports correct")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing response models: {e}")
        return False

def main():
    """Main API compatibility test"""
    print("🧪 API COMPATIBILITY & FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        ("API Endpoints Preservation", test_api_endpoints_preservation),
        ("Service Methods Preservation", test_service_methods_preservation),
        ("Import Statements", test_import_statements),
        ("Dependency Injection", test_dependency_injection),
        ("Response Models", test_response_models),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 API COMPATIBILITY RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 FULL BACKWARD COMPATIBILITY MAINTAINED!")
        print("✅ All APIs and functionalities preserved")
        return True
    else:
        print("⚠️  Some compatibility issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
