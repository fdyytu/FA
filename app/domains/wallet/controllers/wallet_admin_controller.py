"""
Modul ini sekarang hanya berperan sebagai re-export dari admin modules.
Implementasi telah dipindahkan ke modul terpisah di folder admin/.
"""

from app.domains.wallet.controllers.admin import admin_router

# Re-export
router = admin_router.router
__all__ = ['router']
