"""
Modul ini berisi implementasi chart controllers untuk Analytics.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.analytics.controllers.charts.analytics_charts_revenue_controller import router as revenue_router
from app.domains.analytics.controllers.charts.analytics_charts_product_controller import router as product_router
from app.domains.analytics.controllers.charts.analytics_charts_user_controller import router as user_router

# Buat router utama untuk charts
charts_router = APIRouter()

# Include semua sub-routers
charts_router.include_router(revenue_router, prefix="", tags=["Analytics Charts Revenue"])
charts_router.include_router(product_router, prefix="", tags=["Analytics Charts Products"])
charts_router.include_router(user_router, prefix="", tags=["Analytics Charts Users"])

__all__ = ['charts_router']

# Dokumentasi tambahan untuk setiap controller:

# analytics_charts_revenue_controller
# - Menangani endpoint untuk chart revenue
# - Menyediakan data trend revenue
# - Endpoint: /charts/revenue
# - Parameter: days (1-365), group_by (day/week/month)

# analytics_charts_product_controller
# - Menangani endpoint untuk chart produk dan voucher
# - Menyediakan data performa produk dan penggunaan voucher
# - Endpoints: 
#   * /charts/products - Top products berdasarkan revenue
#   * /charts/vouchers - Top vouchers berdasarkan usage

# analytics_charts_user_controller
# - Menangani endpoint untuk chart aktivitas dan retensi user
# - Menyediakan data aktivitas dan cohort analysis
# - Endpoints:
#   * /charts/user-activity - Trend aktivitas login user
#   * /charts/user-retention - Cohort analysis retensi user
