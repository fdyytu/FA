from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from app.common.responses.api_response import create_response
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/revenue", response_model=dict, summary="Get Revenue Analytics")
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """Mendapatkan analytics revenue untuk admin dashboard"""
    try:
        daily_revenue = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            daily_revenue.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "revenue": random.randint(2000000, 6000000),
                "transactions": random.randint(80, 250),
                "average_order_value": random.randint(20000, 35000)
            })
        
        total_revenue = sum(day["revenue"] for day in daily_revenue)
        total_transactions = sum(day["transactions"] for day in daily_revenue)
        
        revenue_data = {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_order_value": round(total_revenue / total_transactions, 2),
            "revenue_growth": 15.8,
            "highest_revenue_day": max(daily_revenue, key=lambda x: x["revenue"]),
            "lowest_revenue_day": min(daily_revenue, key=lambda x: x["revenue"]),
            "revenue_by_category": [
                {"category": "Digital Products", "revenue": total_revenue * 0.45, "percentage": 45.0},
                {"category": "Physical Products", "revenue": total_revenue * 0.35, "percentage": 35.0},
                {"category": "Services", "revenue": total_revenue * 0.20, "percentage": 20.0}
            ],
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "daily_revenue": daily_revenue
        }
        
        return create_response(
            success=True,
            message="Data revenue analytics berhasil diambil",
            data=revenue_data
        )
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil revenue analytics")
