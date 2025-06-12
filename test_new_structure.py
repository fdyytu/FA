#!/usr/bin/env python3
"""
Script untuk menguji struktur baru FA Application.
Memastikan semua import dan dependency berfungsi dengan baik.
"""

import sys
import os
import traceback

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test semua import yang diperlukan"""
    print("🧪 Testing imports...")
    
    try:
        # Test infrastructure imports
        from app.infrastructure.config.settings import settings
        from app.infrastructure.database.database_manager import db_manager
        from app.infrastructure.security.password_handler import PasswordHandler
        from app.infrastructure.security.token_handler import TokenHandler
        print("✅ Infrastructure imports successful")
        
        # Test shared components imports
        from app.shared.base_classes.base_repository import BaseRepository
        from app.shared.base_classes.base_service import BaseService
        from app.shared.base_classes.base_controller import BaseController
        from app.shared.responses.api_response import APIResponse
        from app.shared.dependencies.auth_deps import get_current_user
        print("✅ Shared components imports successful")
        
        # Test auth domain imports
        from app.domains.auth.models.user import User
        from app.domains.auth.repositories.user_repository import UserRepository
        from app.domains.auth.services.auth_service import AuthService
        from app.domains.auth.schemas.auth_schemas import UserCreate, UserResponse
        from app.domains.auth.controllers.auth_controller import auth_controller
        print("✅ Auth domain imports successful")
        
        # Test new main application
        from app.new_main import app
        print("✅ New main application import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        traceback.print_exc()
        return False

def test_configurations():
    """Test konfigurasi aplikasi"""
    print("\n⚙️ Testing configurations...")
    
    try:
        from app.infrastructure.config.settings import settings
        from app.infrastructure.config.auth_config import auth_config
        
        # Test basic settings
        assert settings.APP_NAME == "FA Application"
        assert settings.DATABASE_URL is not None
        print("✅ Basic settings OK")
        
        # Test auth config
        assert auth_config.SECRET_KEY is not None
        assert auth_config.ALGORITHM == "HS256"
        print("✅ Auth config OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test koneksi database"""
    print("\n🗄️ Testing database connection...")
    
    try:
        from app.infrastructure.database.database_manager import db_manager
        
        # Test database manager initialization
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None
        assert db_manager.Base is not None
        print("✅ Database manager initialized")
        
        # Test database session
        db_gen = db_manager.get_db()
        db = next(db_gen)
        assert db is not None
        db.close()
        print("✅ Database session created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_security_components():
    """Test komponen security"""
    print("\n🔐 Testing security components...")
    
    try:
        from app.infrastructure.security.password_handler import PasswordHandler
        from app.infrastructure.security.token_handler import TokenHandler
        
        # Test password handler
        password_handler = PasswordHandler()
        test_password = "TestPassword123!"
        hashed = password_handler.hash_password(test_password)
        assert password_handler.verify_password(test_password, hashed)
        print("✅ Password handler working")
        
        # Test token handler
        token_handler = TokenHandler()
        test_data = {"sub": "testuser", "user_id": 1}
        token = token_handler.create_access_token(test_data)
        assert token is not None
        print("✅ Token handler working")
        
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_api_responses():
    """Test API response format"""
    print("\n📡 Testing API responses...")
    
    try:
        from app.shared.responses.api_response import APIResponse
        
        # Test success response
        success_response = APIResponse.success_response(
            data={"test": "data"},
            message="Test successful"
        )
        assert success_response.success == True
        assert success_response.data == {"test": "data"}
        print("✅ Success response format OK")
        
        # Test error response
        error_response = APIResponse.error_response(
            message="Test error",
            errors={"field": "error message"}
        )
        assert error_response.success == False
        assert error_response.errors == {"field": "error message"}
        print("✅ Error response format OK")
        
        return True
        
    except Exception as e:
        print(f"❌ API response test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_domain_structure():
    """Test struktur domain"""
    print("\n🏗️ Testing domain structure...")
    
    try:
        # Test auth domain structure
        from app.domains.auth.models.user import User
        from app.domains.auth.repositories.user_repository import UserRepository
        from app.domains.auth.services.auth_service import AuthService
        from app.domains.auth.schemas.auth_schemas import UserCreate
        
        # Test model
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == "users"
        print("✅ User model structure OK")
        
        # Test schema
        user_create_schema = UserCreate(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            password="TestPassword123!"
        )
        assert user_create_schema.username == "testuser"
        print("✅ User schema structure OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Domain structure test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting FA Application Structure Tests\n")
    
    tests = [
        test_imports,
        test_configurations,
        test_database_connection,
        test_security_components,
        test_api_responses,
        test_domain_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}")
            failed += 1
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Struktur baru siap digunakan.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
