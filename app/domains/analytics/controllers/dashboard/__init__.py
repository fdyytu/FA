"""
Modul ini berisi implementasi dashboard controllers untuk Analytics.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.analytics.controllers.dashboard.analytics_dashboard_api_controller import router as api_router
from app.domains.analytics.controllers.dashboard.analytics_dashboard_ui_controller import router as ui_router

# Buat router utama untuk dashboard
dashboard_router = APIRouter()

# Include semua sub-routers
dashboard_router.include_router(api_router, prefix="", tags=["Analytics Dashboard API"])
dashboard_router.include_router(ui_router, prefix="", tags=["Analytics Dashboard UI"])

__all__ = ['dashboard_router']

# Dokumentasi tambahan untuk setiap controller:

# analytics_dashboard_api_controller
# - Menangani endpoint API untuk dashboard analytics
# - Menyediakan data summary untuk dashboard
# - Endpoint: /dashboard/summary
# - Parameter: days (1-365)

# analytics_dashboard_ui_controller
# - Menangani tampilan UI dashboard analytics
# - Menyediakan halaman web interaktif
# - Endpoint: /dashboard
# - Fitur:
#   * Visualisasi data dengan Chart.js
#   * Filter periode (7/30/90 hari)
#   * Auto-refresh data
#   * Responsive layout dengan Tailwind CSS
