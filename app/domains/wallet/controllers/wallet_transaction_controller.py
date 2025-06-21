"""
Modul ini sekarang hanya berperan sebagai re-export dari transaction modules.
Implementasi telah dipindahkan ke modul terpisah di folder transaction/.
"""

from app.domains.wallet.controllers.transaction import transaction_router
from fastapi import APIRouter

# Re-export
router = transaction_router

# Create a dummy class for backward compatibility
class WalletTransactionController:
    """
    Dummy class untuk kompatibilitas backward.
    Implementasi sebenarnya ada di transaction modules.
    """
    def __init__(self):
        self.router = transaction_router

__all__ = ['router', 'WalletTransactionController']
