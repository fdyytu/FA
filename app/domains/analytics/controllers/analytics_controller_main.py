"""
Modul ini sekarang hanya berperan sebagai re-export dari core modules.
Implementasi telah dipindahkan ke modul terpisah di folder core/.
"""

from app.domains.analytics.controllers.core.analytics_dependencies import get_analytics_service
from app.domains.analytics.controllers.core.analytics_router import main_router

# Re-export
router = main_router
__all__ = ['router', 'get_analytics_service']
