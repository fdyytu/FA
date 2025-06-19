"""
Modul ini berisi implementasi balance controllers untuk Wallet.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.wallet.controllers.balance.wallet_balance_query_controller import router as query_router

# Buat router utama untuk balance
balance_router = APIRouter()

# Include semua sub-routers
balance_router.include_router(query_router, prefix="", tags=["Wallet Balance"])

__all__ = ['balance_router']

# Dokumentasi tambahan untuk setiap controller:

# wallet_balance_query_controller.py
# - Menangani query untuk wallet balance
# - Endpoint: /balance
# - Method: GET
# - Response: WalletBalanceResponse
# - Features:
#   * Get current user's wallet balance
#   * Requires authentication
#   * Returns balance with user info
