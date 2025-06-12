from fastapi import APIRouter
from . import profile, settings, admin

# Router utama untuk semua endpoint user
user_router = APIRouter()

# Include router untuk user profile (untuk user biasa)
user_router.include_router(profile.router, prefix="", tags=["user-profile"])

# Include router untuk user settings (untuk user biasa)  
user_router.include_router(settings.router, prefix="", tags=["user-settings"])

# Router terpisah untuk admin user management
admin_router = APIRouter()
admin_router.include_router(admin.router, prefix="/admin", tags=["admin-user-management"])
