"""
Modul ini sekarang hanya berperan sebagai re-export dari balance modules.
Implementasi telah dipindahkan ke modul terpisah di folder balance/.
"""

from app.domains.wallet.controllers.balance import balance_router
from fastapi import APIRouter

# Re-export
router = balance_router

# Create a dummy class for backward compatibility
class WalletBalanceController:
    """
    Dummy class untuk kompatibilitas backward.
    Implementasi sebenarnya ada di balance modules.
    """
    def __init__(self):
        self.router = balance_router

__all__ = ['router', 'WalletBalanceController']
