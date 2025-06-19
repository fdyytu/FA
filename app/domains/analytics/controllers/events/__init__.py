"""
Modul ini berisi implementasi event controllers untuk Analytics.
File-file telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from fastapi import APIRouter
from app.domains.analytics.controllers.events.analytics_events_query_controller import router as query_router

# Buat router utama untuk events
events_router = APIRouter()

# Include semua sub-routers
events_router.include_router(query_router, prefix="", tags=["Analytics Events"])

__all__ = ['events_router']

# Dokumentasi tambahan untuk setiap controller:

# analytics_events_query_controller
# - Menangani endpoint untuk query events analytics
# - Menyediakan filtering events berdasarkan berbagai parameter
# - Endpoint: /events
# - Parameter:
#   * start_date: Tanggal mulai filter (optional)
#   * end_date: Tanggal akhir filter (optional)
#   * event_type: Filter berdasarkan tipe event (optional)
#   * user_id: Filter berdasarkan user ID (optional)
#   * product_id: Filter berdasarkan product ID (optional)
#   * voucher_id: Filter berdasarkan voucher ID (optional)
#   * limit: Jumlah maksimal data (1-1000, default: 100)
#   * offset: Offset untuk pagination (default: 0)
