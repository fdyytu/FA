"""
Modul ini berisi implementasi top-up controllers untuk Wallet.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.wallet.controllers.topup.wallet_manual_topup_controller import router as manual_router
from app.domains.wallet.controllers.topup.wallet_midtrans_controller import router as midtrans_router

# Buat router utama untuk top-up
topup_router = APIRouter()

# Include semua sub-routers
topup_router.include_router(manual_router, prefix="", tags=["Wallet Top-up"])
topup_router.include_router(midtrans_router, prefix="", tags=["Wallet Top-up"])

__all__ = ['topup_router']

# Dokumentasi tambahan untuk setiap controller:

# wallet_manual_topup_controller.py
# - Menangani operasi top-up manual
# - Endpoints:
#   * /topup/manual (POST) - Membuat permintaan top-up manual
#   * /topup/manual/{request_id}/upload-proof (POST) - Upload bukti pembayaran
# - Features:
#   * File upload validation
#   * Proof of payment handling
#   * Requires authentication

# wallet_midtrans_controller.py
# - Menangani operasi top-up via Midtrans
# - Endpoints:
#   * /topup/midtrans (POST) - Membuat pembayaran Midtrans
#   * /midtrans/notification (POST) - Handle webhook notifikasi
# - Features:
#   * Payment gateway integration
#   * Webhook handling
#   * Automatic balance update
