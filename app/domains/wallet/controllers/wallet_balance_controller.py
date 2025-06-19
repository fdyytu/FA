"""
Modul ini sekarang hanya berperan sebagai re-export dari balance modules.
Implementasi telah dipindahkan ke modul terpisah di folder balance/.
"""

from app.domains.wallet.controllers.balance import balance_router

# Re-export
router = balance_router
__all__ = ['router']
