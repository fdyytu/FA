from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.common.responses.api_response import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/overview", response_model=dict, summary="Get Analytics Overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """Mendapatkan overview analytics untuk admin dashboard"""
    try:
        overview_data = {
            "total_revenue": 125000000,
            "total_transactions": 4250,
            "total_users": 1850,
            "total_products": 125,
            "revenue_growth": 15.8,
            "transaction_growth": 12.3,
            "user_growth": 8.7,
            "product_growth": 5.2,
            "conversion_rate": 3.4,
            "average_order_value": 29411.76,
            "customer_lifetime_value": 67567.57,
            "churn_rate": 2.1,
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "quick_stats": {
                "today_revenue": 4200000,
                "today_transactions": 142,
                "today_new_users": 23,
                "today_orders": 89
            },
            "trends": {
                "revenue_trend": "up",
                "transaction_trend": "up", 
                "user_trend": "up",
                "conversion_trend": "stable"
            }
        }
        
        return create_response(
            success=True,
            message="Data overview analytics berhasil diambil",
            data=overview_data
        )
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil overview analytics")
