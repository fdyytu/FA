"""
Dashboard Helper Functions
Helper functions untuk dashboard service
Maksimal 50 baris per file
"""

from typing import List, Dict, Any
import logging

from app.domains.admin.schemas.admin_schemas import DashboardResponse, DashboardStats, TransactionStats

logger = logging.getLogger(__name__)


def get_transaction_trends(dashboard_repo, days: int = 7) -> List[TransactionStats]:
    """Get transaction trends dengan error handling"""
    try:
        trends = dashboard_repo.get_transaction_trends(days)
        result = []
        for trend in trends:
            if isinstance(trend, dict):
                result.append(TransactionStats(
                    date=trend.get("date", ""),
                    count=trend.get("count", 0),
                    amount=trend.get("amount", 0)
                ))
        logger.info(f"Retrieved {len(result)} transaction trends")
        return result
    except Exception as e:
        logger.error(f"Error getting transaction trends: {str(e)}", exc_info=True)
        return []


def get_top_products(dashboard_repo, limit: int = 5) -> List[Dict[str, Any]]:
    """Get top products dengan error handling"""
    try:
        products = dashboard_repo.get_top_products(limit)
        logger.info(f"Retrieved {len(products)} top products")
        return products
    except Exception as e:
        logger.error(f"Error getting top products: {str(e)}", exc_info=True)
        return []


def get_empty_dashboard_response() -> DashboardResponse:
    """Return empty dashboard response"""
    empty_stats = DashboardStats(
        total_users=0, active_users=0, total_transactions=0,
        total_revenue=0, pending_transactions=0, failed_transactions=0
    )
    return DashboardResponse(
        stats=empty_stats, recent_transactions=[],
        transaction_trends=[], top_products=[]
    )
