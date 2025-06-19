"""
Modul ini berisi implementasi controller untuk Wallet.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.wallet.controllers.wallet_controller_main import router as wallet_router
from app.domains.wallet.controllers.wallet_balance_controller import WalletBalanceController
from app.domains.wallet.controllers.wallet_transaction_controller import WalletTransactionController
from app.domains.wallet.controllers.wallet_topup_controller import WalletTopUpController
from app.domains.wallet.controllers.wallet_admin_controller import WalletAdminController

# Mengekspor router utama yang sudah mencakup semua sub-router
router = wallet_router

__all__ = [
    'router',  # Router utama yang mengintegrasikan semua endpoint
    'WalletBalanceController',  # Controller untuk operasi saldo
    'WalletTransactionController',  # Controller untuk operasi transaksi
    'WalletTopUpController',  # Controller untuk operasi top-up
    'WalletAdminController'  # Controller untuk operasi admin
]

# Dokumentasi tambahan untuk setiap controller:

# WalletBalanceController
# - Menangani endpoint untuk melihat saldo wallet
# - Implementasi Single Responsibility untuk operasi saldo

# WalletTransactionController
# - Menangani endpoint untuk transaksi dan transfer
# - Menyediakan riwayat transaksi
# - Implementasi Single Responsibility untuk operasi transaksi

# WalletTopUpController
# - Menangani endpoint untuk top-up manual dan Midtrans
# - Mengelola upload bukti pembayaran
# - Implementasi Single Responsibility untuk operasi top-up

# WalletAdminController
# - Menangani endpoint khusus admin
# - Mengelola persetujuan top-up
# - Implementasi Single Responsibility untuk operasi admin
