"""
Modul ini berisi implementasi service untuk Wallet.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.wallet.services.wallet_service import WalletService
from app.domains.wallet.services.wallet_transaction_service import WalletTransactionService
from app.domains.wallet.services.wallet_transfer_service import WalletTransferService
from app.domains.wallet.services.wallet_topup_service import WalletTopUpService
from app.domains.wallet.services.wallet_admin_service import WalletAdminService

__all__ = [
    'WalletService',  # Service utama yang mengintegrasikan semua sub-service
    'WalletTransactionService',  # Service untuk transaksi dasar
    'WalletTransferService',  # Service untuk transfer
    'WalletTopUpService',  # Service untuk top-up
    'WalletAdminService'  # Service untuk admin
]

# Dokumentasi tambahan untuk setiap service:

# WalletService
# - Service utama yang mengimplementasikan Facade Pattern
# - Menyederhanakan interface ke subsystem wallet
# - Mengintegrasikan semua sub-service

# WalletTransactionService
# - Menangani operasi transaksi dasar
# - Mengelola saldo dan riwayat transaksi
# - Menyediakan statistik wallet

# WalletTransferService
# - Menangani operasi transfer antar user
# - Memvalidasi transfer dan saldo
# - Mencatat transaksi transfer

# WalletTopUpService
# - Menangani operasi top-up manual dan Midtrans
# - Memproses bukti pembayaran
# - Mengelola notifikasi pembayaran

# WalletAdminService
# - Menangani operasi khusus admin
# - Mengelola persetujuan top-up
# - Menyediakan data untuk admin
