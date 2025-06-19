"""
Modul ini berisi implementasi controller untuk Analytics.
File ini telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.analytics.controllers.analytics_controller import router as analytics_router
from app.domains.analytics.controllers.analytics_controller import admin_analytics_router
from app.domains.analytics.controllers.analytics_events_controller import router as events_router
from app.domains.analytics.controllers.analytics_tracking_controller import router as tracking_router
from app.domains.analytics.controllers.analytics_controller_admin import router as admin_router

# Mengekspor router utama yang sudah mencakup semua sub-router
router = analytics_router

__all__ = [
    'router',  # Router utama yang mengintegrasikan semua endpoint
    'analytics_router',  # Router untuk endpoint analytics umum
    'events_router',  # Router untuk endpoint events
    'tracking_router',  # Router untuk endpoint tracking
    'admin_router',  # Router untuk endpoint admin
    'admin_analytics_router'  # Router untuk endpoint admin analytics
]
