"""
Modul ini sekarang hanya berperan sebagai re-export dari topup modules.
Implementasi telah dipindahkan ke modul terpisah di folder topup/.
"""

from app.domains.wallet.controllers.topup import topup_router
from fastapi import APIRouter

# Re-export
router = topup_router

# Create a dummy class for backward compatibility
class WalletTopUpController:
    """
    Dummy class untuk kompatibilitas backward.
    Implementasi sebenarnya ada di topup modules.
    """
    def __init__(self):
        self.router = topup_router

__all__ = ['router', 'WalletTopUpController']
