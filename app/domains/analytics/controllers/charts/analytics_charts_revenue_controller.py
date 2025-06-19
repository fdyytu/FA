from fastapi import APIRouter, Depends, HTTPException, Query
from app.domains.analytics.services.analytics_service import AnalyticsService
from app.common.responses.api_response import create_response
from app.domains.analytics.controllers.analytics_controller_main import get_analytics_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/charts/revenue", response_model=dict, summary="Get Revenue Chart Data")
async def get_revenue_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    group_by: str = Query("day", regex="^(day|week|month)$", description="Grouping periode"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk revenue trend.
    
    - **days**: Periode analisis dalam hari
    - **group_by**: Grouping data (day, week, month)
    """
    try:
        chart_data = await service.get_revenue_chart_data(days, group_by)
        
        return create_response(
            success=True,
            message="Data chart revenue berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting revenue chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart revenue")
