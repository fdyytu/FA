from fastapi import APIRouter, Depends, HTTPException, Query
from app.domains.analytics.services.analytics_service import AnalyticsService
from app.common.responses.api_response import create_response
from app.domains.analytics.controllers.analytics_controller_main import get_analytics_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/charts/user-activity", response_model=dict, summary="Get User Activity Chart")
async def get_user_activity_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk aktivitas user.
    
    Menampilkan trend login harian user.
    """
    try:
        chart_data = await service.get_user_activity_chart(days)
        
        return create_response(
            success=True,
            message="Data chart aktivitas user berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting user activity chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart aktivitas user")

@router.get("/charts/user-retention", response_model=dict, summary="Get User Retention Chart")
async def get_user_retention_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk retensi user.
    
    Menampilkan cohort analysis untuk retensi user.
    """
    try:
        chart_data = await service.get_user_retention_chart(days)
        
        return create_response(
            success=True,
            message="Data chart retensi user berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets,
                "cohort_data": chart_data.cohort_data
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting user retention chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart retensi user")
