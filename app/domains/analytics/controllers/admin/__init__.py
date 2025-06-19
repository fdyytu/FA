"""
Modul ini berisi implementasi admin controllers untuk Analytics.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.analytics.controllers.admin.analytics_admin_overview_controller import router as overview_router
from app.domains.analytics.controllers.admin.analytics_admin_revenue_controller import router as revenue_router
from app.domains.analytics.controllers.admin.analytics_admin_user_controller import router as user_router
from app.domains.analytics.controllers.admin.analytics_admin_performance_controller import router as performance_router

admin_router = APIRouter()

admin_router.include_router(overview_router, prefix="", tags=["Analytics Admin Overview"])
admin_router.include_router(revenue_router, prefix="", tags=["Analytics Admin Revenue"])
admin_router.include_router(user_router, prefix="", tags=["Analytics Admin User"])
admin_router.include_router(performance_router, prefix="", tags=["Analytics Admin Performance"])

__all__ = ['admin_router']

# Dokumentasi tambahan untuk setiap controller:

# analytics_admin_overview_controller.py
# - Endpoint: /overview
# - Method: GET
# - Menyediakan data overview analytics untuk dashboard admin

# analytics_admin_revenue_controller.py
# - Endpoint: /revenue
# - Method: GET
# - Menyediakan data revenue analytics

# analytics_admin_user_controller.py
# - Endpoint: /users
# - Method: GET
# - Menyediakan data user analytics

# analytics_admin_performance_controller.py
# - Endpoint: /performance
# - Method: GET
# - Menyediakan data performance analytics
