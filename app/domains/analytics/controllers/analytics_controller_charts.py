"""
Modul ini sekarang hanya berperan sebagai re-export dari chart controllers.
Implementasi telah dipindahkan ke modul terpisah di folder charts/.
"""

from app.domains.analytics.controllers.charts import charts_router

# Re-export charts_router
router = charts_router
__all__ = ['router']
