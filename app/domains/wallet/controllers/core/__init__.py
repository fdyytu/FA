"""
Modul ini berisi implementasi core functionality untuk Wallet controllers.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.wallet.controllers.core.wallet_router import main_router

__all__ = ['main_router']

# Dokumentasi tambahan untuk setiap modul:

# wallet_router.py
# - Menangani setup router utama untuk Wallet
# - Mengintegrasikan semua sub-routers:
#   * Balance router
#   * Transaction router
#   * Top-up router
#   * Admin router (prefix: /admin)
# - Mengatur prefix (/wallet) dan tags untuk semua routes
