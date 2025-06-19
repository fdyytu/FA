"""
Modul ini berisi dependency injection untuk Analytics controllers.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.analytics.services.analytics_service import AnalyticsService
import logging

logger = logging.getLogger(__name__)

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Dependency untuk mendapatkan AnalyticsService"""
    return AnalyticsService(db)

__all__ = ['get_analytics_service']
