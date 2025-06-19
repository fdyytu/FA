"""
Modul ini sekarang hanya berperan sebagai re-export dari topup modules.
Implementasi telah dipindahkan ke modul terpisah di folder topup/.
"""

from app.domains.wallet.controllers.topup import topup_router

# Re-export
router = topup_router.router
__all__ = ['router']
