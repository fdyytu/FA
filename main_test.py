"""
Working main application file for user management API testing
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="FA User Management API",
        description="User Management API with SOLID principles",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Mock database dependency for testing
    def get_mock_db():
        """Mock database session for testing"""
        return None
    
    # Mock current user dependency for testing
    def get_mock_current_user():
        """Mock current user for testing"""
        class MockUser:
            id = 1
            username = "test_user"
            email = "test@example.com"
            full_name = "Test User"
            is_admin = False
            is_active = True
        return MockUser()
    
    def get_mock_admin_user():
        """Mock admin user for testing"""
        class MockAdminUser:
            id = 1
            username = "admin_user"
            email = "admin@example.com"
            full_name = "Admin User"
            is_admin = True
            is_active = True
        return MockAdminUser()
    
    # User Profile Endpoints
    @app.get("/api/v1/users/profile", tags=["User Profile"])
    async def get_user_profile(current_user=Depends(get_mock_current_user)):
        """Get user profile"""
        return {
            "success": True,
            "data": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "phone_number": "+6281234567890",
                "balance": 100000.0,
                "is_active": current_user.is_active,
                "created_at": "2024-01-01T00:00:00",
                "profile": {
                    "id": 1,
                    "user_id": current_user.id,
                    "avatar_url": "/static/uploads/avatars/1_avatar.jpg",
                    "birth_date": "1990-01-01T00:00:00",
                    "address": "Jl. Sudirman No. 1",
                    "city": "Jakarta",
                    "province": "DKI Jakarta",
                    "postal_code": "12345",
                    "identity_verified": "verified"
                }
            },
            "message": "Profil berhasil diambil"
        }
    
    @app.post("/api/v1/users/profile", tags=["User Profile"])
    async def create_user_profile(current_user=Depends(get_mock_current_user)):
        """Create user profile"""
        return {
            "success": True,
            "data": {"id": 1, "user_id": current_user.id},
            "message": "Profil berhasil dibuat"
        }
    
    @app.put("/api/v1/users/profile", tags=["User Profile"])
    async def update_user_profile(current_user=Depends(get_mock_current_user)):
        """Update user profile"""
        return {
            "success": True,
            "data": {"id": 1, "user_id": current_user.id},
            "message": "Profil berhasil diupdate"
        }
    
    # User Settings Endpoints
    @app.get("/api/v1/users/settings", tags=["User Settings"])
    async def get_user_settings(current_user=Depends(get_mock_current_user)):
        """Get user settings"""
        return {
            "success": True,
            "data": {
                "notifications": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "transaction_alerts": True,
                    "marketing_emails": False
                },
                "privacy": {
                    "profile_visibility": "public",
                    "show_balance": False,
                    "show_transaction_history": False
                },
                "security": {
                    "two_factor_enabled": False,
                    "login_alerts": True,
                    "session_timeout": 30
                }
            },
            "message": "Pengaturan berhasil diambil"
        }
    
    @app.put("/api/v1/users/settings", tags=["User Settings"])
    async def update_user_settings(current_user=Depends(get_mock_current_user)):
        """Update user settings"""
        return {
            "success": True,
            "message": "Pengaturan berhasil diupdate"
        }
    
    @app.post("/api/v1/users/change-password", tags=["User Security"])
    async def change_password(current_user=Depends(get_mock_current_user)):
        """Change user password"""
        return {
            "success": True,
            "message": "Password berhasil diubah"
        }
    
    @app.get("/api/v1/users/security", tags=["User Security"])
    async def get_security_settings(current_user=Depends(get_mock_current_user)):
        """Get security settings"""
        return {
            "success": True,
            "data": {
                "two_factor_enabled": False,
                "login_alerts": True,
                "session_timeout": 30,
                "last_password_change": "2024-01-01T00:00:00",
                "active_sessions": 1
            },
            "message": "Pengaturan keamanan berhasil diambil"
        }
    
    @app.post("/api/v1/users/enable-2fa", tags=["User Security"])
    async def enable_2fa(current_user=Depends(get_mock_current_user)):
        """Enable 2FA"""
        return {
            "success": True,
            "data": {
                "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            },
            "message": "2FA berhasil diaktifkan"
        }
    
    # Admin Endpoints
    @app.get("/api/v1/users/admin/users", tags=["Admin"])
    async def get_users_list(
        page: int = 1,
        limit: int = 10,
        search: str = None,
        status: str = "all",
        current_user=Depends(get_mock_admin_user)
    ):
        """Get users list (admin only)"""
        return {
            "success": True,
            "data": {
                "users": [
                    {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "phone_number": "+6281234567890",
                        "balance": 100000.0,
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00",
                        "total_transactions": 25
                    },
                    {
                        "id": 2,
                        "username": "jane_doe",
                        "email": "jane@example.com",
                        "full_name": "Jane Doe",
                        "phone_number": "+6281234567891",
                        "balance": 50000.0,
                        "is_active": True,
                        "created_at": "2024-01-02T00:00:00",
                        "total_transactions": 15
                    }
                ],
                "page": page,
                "limit": limit,
                "total": 2,
                "total_pages": 1
            },
            "message": "Daftar user berhasil diambil"
        }
    
    @app.get("/api/v1/users/admin/users/{user_id}", tags=["Admin"])
    async def get_user_detail(user_id: int, current_user=Depends(get_mock_admin_user)):
        """Get user detail (admin only)"""
        return {
            "success": True,
            "data": {
                "id": user_id,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "phone_number": "+6281234567890",
                "balance": 100000.0,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00",
                "profile": {
                    "address": "Jl. Sudirman No. 1",
                    "city": "Jakarta",
                    "identity_verified": "verified"
                }
            },
            "message": "Detail user berhasil diambil"
        }
    
    @app.get("/api/v1/users/admin/statistics", tags=["Admin"])
    async def get_user_statistics(current_user=Depends(get_mock_admin_user)):
        """Get user statistics (admin only)"""
        return {
            "success": True,
            "data": {
                "total_users": 1000,
                "active_users": 850,
                "inactive_users": 150,
                "top_balance_users": [
                    {
                        "id": 1,
                        "username": "john_doe",
                        "full_name": "John Doe",
                        "balance": 1000000.0
                    }
                ],
                "monthly_registrations": [
                    {"month": "2024-01", "count": 50},
                    {"month": "2024-02", "count": 75}
                ]
            },
            "message": "Statistik user berhasil diambil"
        }
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Basic health check"""
        return {
            "status": "healthy",
            "service": "FA User Management API",
            "version": "1.0.0"
        }
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "FA User Management API",
            "docs": "/docs",
            "health": "/health",
            "endpoints": {
                "user_profile": "/api/v1/users/profile",
                "user_settings": "/api/v1/users/settings",
                "admin_users": "/api/v1/users/admin/users",
                "admin_statistics": "/api/v1/users/admin/statistics"
            }
        }
    
    return app

# Create application instance
app = create_application()

if __name__ == "__main__":
    """Run application directly"""
    uvicorn.run(
        "main_test:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
