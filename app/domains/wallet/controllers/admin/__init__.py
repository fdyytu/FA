"""
Modul ini berisi implementasi admin controllers untuk Wallet.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.wallet.controllers.admin.wallet_topup_approval_controller import router as approval_router

# Buat router utama untuk admin
admin_router = APIRouter()

# Include semua sub-routers
admin_router.include_router(approval_router, prefix="", tags=["Wallet Admin"])

__all__ = ['admin_router']

# Dokumentasi tambahan untuk setiap controller:

# wallet_topup_approval_controller.py
# - Menangani operasi admin untuk approval top-up
# - Endpoints:
#   * /topup-requests (GET) - Mendapatkan daftar permintaan top-up
#   * /topup-requests/{request_id}/approve (PUT) - Approve/reject permintaan
# - Features:
#   * Admin authentication
#   * Pagination support
#   * Request approval/rejection
#   * Automatic balance update on approval
