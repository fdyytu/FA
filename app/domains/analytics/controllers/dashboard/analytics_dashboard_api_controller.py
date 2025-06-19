from fastapi import APIRouter, Depends, HTTPException, Query
from app.domains.analytics.services.analytics_service import AnalyticsService
from app.common.responses.api_response import create_response
from app.domains.analytics.controllers.analytics_controller_main import get_analytics_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard/summary", response_model=dict, summary="Get Dashboard Summary")
async def get_dashboard_summary(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan summary data untuk dashboard analytics.
    
    Menampilkan:
    - Total revenue
    - Total transaksi
    - Total users
    - Growth metrics
    - Top products dan vouchers
    """
    try:
        summary = await service.get_dashboard_summary(days)
        
        return create_response(
            success=True,
            message="Dashboard summary berhasil diambil",
            data={
                "total_revenue": float(summary.total_revenue),
                "total_transactions": summary.total_transactions,
                "total_users": summary.total_users,
                "total_products": summary.total_products,
                "revenue_growth": float(summary.revenue_growth) if summary.revenue_growth else None,
                "transaction_growth": float(summary.transaction_growth) if summary.transaction_growth else None,
                "user_growth": float(summary.user_growth) if summary.user_growth else None,
                "top_products": summary.top_products,
                "top_vouchers": summary.top_vouchers,
                "period_days": days
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil dashboard summary")
