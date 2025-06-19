"""
Modul ini berisi implementasi admin controllers untuk Analytics.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.analytics.controllers.admin.analytics_admin_overview_controller import router as overview_router
from app.domains.analytics.controllers.admin.analytics_admin_revenue_controller import router as revenue_router
from app.domains.analytics.controllers.admin.analytics_admin_user_controller import router as user_router
from app.domains.analytics.controllers.admin.analytics_admin_performance_controller import router as performance_router

# Buat router utama untuk admin analytics
admin_analytics_router = APIRouter()

# Include semua sub-routers
admin_analytics_router.include_router(overview_router, prefix="", tags=["Admin Analytics Overview"])
admin_analytics_router.include_router(revenue_router, prefix="", tags=["Admin Analytics Revenue"])
admin_analytics_router.include_router(user_router, prefix="", tags=["Admin Analytics Users"])
admin_analytics_router.include_router(performance_router, prefix="", tags=["Admin Analytics Performance"])

__all__ = ['admin_analytics_router']

# Dokumentasi tambahan untuk setiap controller:

# analytics_admin_overview_controller
# - Menangani endpoint untuk overview analytics
# - Menyediakan rangkuman metrik utama
# - Endpoint: /overview

# analytics_admin_revenue_controller
# - Menangani endpoint untuk analisis revenue
# - Menyediakan data revenue harian dan trend
# - Endpoint: /revenue

# analytics_admin_user_controller
# - Menangani endpoint untuk analisis user
# - Menyediakan data pertumbuhan dan retensi user
# - Endpoints: /user-growth, /user-retention

# analytics_admin_performance_controller
# - Menangani endpoint untuk performance metrics
# - Menyediakan data performa sistem dan transaksi
# - Endpoints: /performance-metrics, /system-health
