"""
Modul ini berisi implementasi auth controllers untuk Admin.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.admin.controllers.auth.admin_login_controller import router as login_router
from app.domains.admin.controllers.auth.admin_logout_controller import router as logout_router

# Buat router utama untuk auth
auth_router = APIRouter()

# Include semua sub-routers
auth_router.include_router(login_router, prefix="", tags=["Admin Auth"])
auth_router.include_router(logout_router, prefix="", tags=["Admin Auth"])

__all__ = ['auth_router']

# Dokumentasi tambahan untuk setiap controller:

# admin_login_controller.py
# - Menangani operasi login admin
# - Endpoint: /login
# - Method: POST
# - Features:
#   * Admin authentication
#   * JWT token generation
#   * Response dengan admin info

# admin_logout_controller.py
# - Menangani operasi logout admin
# - Endpoint: /logout
# - Method: POST
# - Features:
#   * Audit logging
#   * Requires authentication
