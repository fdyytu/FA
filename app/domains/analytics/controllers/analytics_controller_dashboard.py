"""
Modul ini sekarang hanya berperan sebagai re-export dari dashboard controllers.
Implementasi telah dipindahkan ke modul terpisah di folder dashboard/.
"""

from app.domains.analytics.controllers.dashboard import dashboard_router

# Re-export dashboard_router
router = dashboard_router
__all__ = ['router']
