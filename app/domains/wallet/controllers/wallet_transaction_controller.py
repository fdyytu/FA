"""
Modul ini sekarang hanya berperan sebagai re-export dari transaction modules.
Implementasi telah dipindahkan ke modul terpisah di folder transaction/.
"""

from app.domains.wallet.controllers.transaction import transaction_router

# Re-export
router = transaction_router
__all__ = ['router']
