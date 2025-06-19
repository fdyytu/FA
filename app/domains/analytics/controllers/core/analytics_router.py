"""
Modul ini berisi setup router utama untuk Analytics controllers.
"""

from fastapi import APIRouter

# Import semua router dari modul lain
from app.domains.analytics.controllers.events import events_router
from app.domains.analytics.controllers.dashboard import dashboard_router
from app.domains.analytics.controllers.charts import charts_router
from app.domains.analytics.controllers.admin import admin_analytics_router

# Buat router utama untuk analytics
main_router = APIRouter()

# Include semua router
main_router.include_router(events_router, prefix="", tags=["Analytics Events"])
main_router.include_router(dashboard_router, prefix="", tags=["Analytics Dashboard"])
main_router.include_router(charts_router, prefix="", tags=["Analytics Charts"])
main_router.include_router(admin_analytics_router, prefix="/admin", tags=["Admin Analytics"])

__all__ = ['main_router']
