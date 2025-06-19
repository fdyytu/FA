"""
Modul ini berisi implementasi transaction controllers untuk Wallet.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.wallet.controllers.transaction.wallet_transaction_query_controller import router as query_router
from app.domains.wallet.controllers.transaction.wallet_transfer_controller import router as transfer_router

# Buat router utama untuk transaction
transaction_router = APIRouter()

# Include semua sub-routers
transaction_router.include_router(query_router, prefix="", tags=["Wallet Transactions"])
transaction_router.include_router(transfer_router, prefix="", tags=["Wallet Transactions"])

__all__ = ['transaction_router']

# Dokumentasi tambahan untuk setiap controller:

# wallet_transaction_query_controller.py
# - Menangani query untuk riwayat transaksi
# - Endpoint: /transactions
# - Method: GET
# - Features:
#   * Pagination support
#   * Filter by transaction type
#   * Requires authentication

# wallet_transfer_controller.py
# - Menangani operasi transfer antar user
# - Endpoint: /transfer
# - Method: POST
# - Features:
#   * Transfer validation
#   * Balance checking
#   * Transaction recording
#   * Requires authentication
