from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.domains.analytics.services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

class AnalyticsController:
    """Controller untuk analytics Discord"""
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk analytics"""
        
        @self.router.get("/stats")
        async def get_analytics_stats(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil statistik analytics Discord"""
            try:
                # Get real analytics data from database
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                # Get analytics data
                stats = {
                    "total_events": 0,
                    "total_commands": 0,
                    "total_users": 0,
                    "total_guilds": 0,
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "daily_stats": [],
                    "command_stats": [],
                    "user_stats": [],
                    "error_stats": []
                }
                
                try:
                    # Try to get real analytics data
                    stats = analytics_service.get_dashboard_stats(db, start_date, end_date)
                except Exception as e:
                    logger.warning(f"Could not get analytics data: {e}")
                    # Return empty stats if analytics service is not available
                
                return {
                    "success": True,
                    "data": stats,
                    "period": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat()
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting analytics stats: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Gagal mengambil statistik analytics: {str(e)}"
                )
        
        @self.router.get("/events")
        async def get_analytics_events(
            limit: int = 100,
            event_type: str = None,
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil event analytics"""
            try:
                events = []
                
                try:
                    # Try to get real events data
                    events = analytics_service.get_recent_events(db, limit, event_type)
                except Exception as e:
                    logger.warning(f"Could not get events data: {e}")
                
                return {
                    "success": True,
                    "data": {
                        "events": events,
                        "total": len(events),
                        "limit": limit,
                        "event_type": event_type
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting analytics events: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Gagal mengambil event analytics: {str(e)}"
                )
        
        @self.router.get("/metrics")
        async def get_analytics_metrics(
            db: Session = Depends(get_db)
        ) -> Dict[str, Any]:
            """Ambil metrics analytics"""
            try:
                metrics = {
                    "performance": {
                        "avg_response_time": 0.0,
                        "success_rate": 0.0,
                        "error_rate": 0.0
                    },
                    "usage": {
                        "total_commands": 0,
                        "active_users": 0,
                        "active_guilds": 0
                    },
                    "trends": {
                        "daily_growth": 0.0,
                        "weekly_growth": 0.0,
                        "monthly_growth": 0.0
                    }
                }
                
                try:
                    # Try to get real metrics data
                    metrics = analytics_service.get_performance_metrics(db)
                except Exception as e:
                    logger.warning(f"Could not get metrics data: {e}")
                
                return {
                    "success": True,
                    "data": metrics
                }
                
            except Exception as e:
                logger.error(f"Error getting analytics metrics: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Gagal mengambil metrics analytics: {str(e)}"
                )

# Initialize controller
analytics_controller = AnalyticsController()

# Export router untuk kompatibilitas dengan import
router = analytics_controller.router
