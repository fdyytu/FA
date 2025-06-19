"""
Modul ini berisi implementasi controller untuk Analytics.
File ini telah dipecah menjadi beberapa modul yang lebih kecil untuk meningkatkan maintainability.
"""

from app.domains.analytics.controllers.analytics_controller_main import router as analytics_router
from app.domains.analytics.controllers.analytics_controller_events import router as events_router
from app.domains.analytics.controllers.analytics_controller_dashboard import router as dashboard_router
from app.domains.analytics.controllers.analytics_controller_charts import router as charts_router
from app.domains.analytics.controllers.analytics_controller_admin import admin_analytics_router

# Mengekspor router utama yang sudah mencakup semua sub-router
router = analytics_router

__all__ = [
    'router',  # Router utama yang mengintegrasikan semua endpoint
    'analytics_router',  # Router untuk endpoint analytics umum
    'events_router',  # Router untuk endpoint events
    'dashboard_router',  # Router untuk endpoint dashboard
    'charts_router',  # Router untuk endpoint charts
    'admin_analytics_router'  # Router untuk endpoint admin analytics
]
