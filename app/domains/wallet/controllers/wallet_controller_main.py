"""
Modul ini sekarang hanya berperan sebagai re-export dari core modules.
Implementasi telah dipindahkan ke modul terpisah di folder core/.
"""

from app.domains.wallet.controllers.core import main_router

# Re-export
router = main_router
__all__ = ['router']
