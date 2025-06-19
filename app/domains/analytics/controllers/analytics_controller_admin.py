"""
Modul ini sekarang hanya berperan sebagai re-export dari admin controllers.
Implementasi telah dipindahkan ke modul terpisah di folder admin/.
"""

from app.domains.analytics.controllers.admin import admin_analytics_router

# Re-export admin_analytics_router
__all__ = ['admin_analytics_router']
