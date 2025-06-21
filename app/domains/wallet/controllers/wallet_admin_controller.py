"""
Modul ini sekarang hanya berperan sebagai re-export dari admin modules.
Implementasi telah dipindahkan ke modul terpisah di folder admin/.
"""

from app.domains.wallet.controllers.admin import admin_router
from fastapi import APIRouter

# Re-export
router = admin_router

# Create a dummy class for backward compatibility
class WalletAdminController:
    """
    Dummy class untuk kompatibilitas backward.
    Implementasi sebenarnya ada di admin modules.
    """
    def __init__(self):
        self.router = admin_router

__all__ = ['router', 'WalletAdminController']
