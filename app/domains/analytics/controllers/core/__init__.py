"""
Modul ini berisi implementasi core functionality untuk Analytics controllers.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.analytics.controllers.core.analytics_dependencies import get_analytics_service
from app.domains.analytics.controllers.core.analytics_router import main_router

__all__ = ['get_analytics_service', 'main_router']

# Dokumentasi tambahan untuk setiap modul:

# analytics_dependencies.py
# - Menangani dependency injection untuk Analytics
# - Menyediakan service dependencies
# - Fungsi: get_analytics_service

# analytics_router.py
# - Menangani setup router utama untuk Analytics
# - Mengintegrasikan semua sub-routers:
#   * Events router (/events)
#   * Dashboard router (/dashboard)
#   * Charts router (/charts)
#   * Admin router (/admin)
# - Mengatur prefix dan tags untuk setiap router
