from fastapi import APIRouter, Depends, HTTPException, Query
from app.domains.analytics.services.analytics_service import AnalyticsService
from app.common.responses.api_response import create_response
from app.domains.analytics.controllers.analytics_controller_main import get_analytics_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/charts/products", response_model=dict, summary="Get Product Performance Chart")
async def get_product_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk performa produk.
    
    Menampilkan top products berdasarkan revenue.
    """
    try:
        chart_data = await service.get_product_performance_chart(days)
        
        return create_response(
            success=True,
            message="Data chart produk berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting product chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart produk")

@router.get("/charts/vouchers", response_model=dict, summary="Get Voucher Usage Chart")
async def get_voucher_chart(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan data chart untuk penggunaan voucher.
    
    Menampilkan top vouchers berdasarkan usage count.
    """
    try:
        chart_data = await service.get_voucher_usage_chart(days)
        
        return create_response(
            success=True,
            message="Data chart voucher berhasil diambil",
            data={
                "title": chart_data.title,
                "chart_type": chart_data.chart_type,
                "labels": chart_data.labels,
                "datasets": chart_data.datasets
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting voucher chart: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data chart voucher")
