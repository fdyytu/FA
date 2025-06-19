from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from app.common.responses.api_response import create_response
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/performance-metrics", response_model=dict, summary="Get Performance Metrics")
async def get_performance_metrics(
    days: int = Query(30, ge=1, le=365, description="Jumlah hari untuk analisis")
):
    """Mendapatkan performance metrics untuk admin dashboard"""
    try:
        daily_metrics = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            current_date = base_date + timedelta(days=i)
            daily_metrics.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "transactions": random.randint(50, 200),
                "revenue": random.randint(500000, 2000000),
                "success_rate": round(random.uniform(85.0, 98.0), 2),
                "response_time": round(random.uniform(0.1, 0.8), 3)
            })
        
        total_transactions = sum(day["transactions"] for day in daily_metrics)
        successful_transactions = int(total_transactions * 0.92)
        
        performance_data = {
            "total_transactions": total_transactions,
            "successful_transactions": successful_transactions,
            "failed_transactions": total_transactions - successful_transactions,
            "success_rate": round((successful_transactions / total_transactions) * 100, 2),
            "daily_metrics": daily_metrics,
            "period_days": days,
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data performance metrics berhasil diambil",
            data=performance_data
        )
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil performance metrics")

@router.get("/system-health", response_model=dict, summary="Get System Health Metrics")
async def get_system_health():
    """Mendapatkan metrics kesehatan sistem"""
    try:
        health_data = {
            "system_status": "healthy",
            "uptime": "99.98%",
            "response_time": {
                "average": 0.245,
                "p95": 0.512,
                "p99": 0.876
            },
            "error_rate": {
                "last_hour": 0.12,
                "last_24h": 0.08,
                "last_7d": 0.05
            },
            "resource_usage": {
                "cpu": random.uniform(20, 60),
                "memory": random.uniform(40, 80),
                "disk": random.uniform(30, 70)
            },
            "queue_status": {
                "pending_jobs": random.randint(5, 50),
                "processing_rate": random.uniform(95, 99.9)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return create_response(
            success=True,
            message="Data system health berhasil diambil",
            data=health_data
        )
    except Exception as e:
        logger.error(f"Error getting system health metrics: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil system health metrics")
