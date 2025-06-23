from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.domains.analytics.repositories.analytics_repository import AnalyticsRepository
from app.domains.analytics.schemas.analytics_schemas import (
    AnalyticsEventCreate, AnalyticsFilter, DashboardSummary, ChartData, ChartDataPoint
)
from app.domains.analytics.models.analytics import AnalyticsEvent
from app.common.base_classes.base_service import BaseService
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class AnalyticsService(BaseService):
    """
    Service untuk menangani business logic analytics.
    Mengimplementasikan Single Responsibility Principle.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AnalyticsRepository(db)
    
    async def track_event(self, event_data: AnalyticsEventCreate) -> AnalyticsEvent:
        """Track event analytics baru"""
        try:
            return self.repository.create_event(event_data)
        except Exception as e:
            logger.error(f"Error tracking analytics event: {e}")
            raise
    
    async def get_events(self, filter_params: AnalyticsFilter, 
                        limit: int = 100, offset: int = 0) -> List[AnalyticsEvent]:
        """Mendapatkan events berdasarkan filter"""
        try:
            return self.repository.get_events_by_filter(filter_params, limit, offset)
        except Exception as e:
            logger.error(f"Error getting analytics events: {e}")
            raise
    
    async def get_dashboard_summary(self, days: int = 30) -> DashboardSummary:
        """Mendapatkan summary untuk dashboard"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get revenue data
            revenue_data = self.repository.get_revenue_by_period(start_date, end_date)
            total_revenue = sum(item['total_revenue'] for item in revenue_data)
            total_transactions = sum(item['transaction_count'] for item in revenue_data)
            
            # Get user stats
            user_stats = self.repository.get_user_activity_stats(start_date, end_date)
            
            # Get top products and vouchers
            top_products = self.repository.get_top_products(start_date, end_date, limit=5)
            top_vouchers = self.repository.get_top_vouchers(start_date, end_date, limit=5)
            
            # Calculate growth (compare with previous period)
            prev_start_date = start_date - timedelta(days=days)
            prev_revenue_data = self.repository.get_revenue_by_period(prev_start_date, start_date)
            prev_total_revenue = sum(item['total_revenue'] for item in prev_revenue_data)
            prev_total_transactions = sum(item['transaction_count'] for item in prev_revenue_data)
            prev_user_stats = self.repository.get_user_activity_stats(prev_start_date, start_date)
            
            # Calculate growth percentages
            revenue_growth = None
            if prev_total_revenue > 0:
                revenue_growth = ((total_revenue - prev_total_revenue) / prev_total_revenue) * 100
            
            transaction_growth = None
            if prev_total_transactions > 0:
                transaction_growth = ((total_transactions - prev_total_transactions) / prev_total_transactions) * 100
            
            user_growth = None
            if prev_user_stats['unique_users'] > 0:
                user_growth = ((user_stats['unique_users'] - prev_user_stats['unique_users']) / prev_user_stats['unique_users']) * 100
            
            return DashboardSummary(
                total_revenue=Decimal(str(total_revenue)),
                total_transactions=total_transactions,
                total_users=user_stats['unique_users'],
                total_products=len(top_products),
                revenue_growth=Decimal(str(revenue_growth)) if revenue_growth is not None else None,
                transaction_growth=Decimal(str(transaction_growth)) if transaction_growth is not None else None,
                user_growth=Decimal(str(user_growth)) if user_growth is not None else None,
                top_products=top_products,
                top_vouchers=top_vouchers
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            raise
    
    async def get_revenue_chart_data(self, days: int = 30, group_by: str = "day") -> ChartData:
        """Mendapatkan data chart revenue"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            revenue_data = self.repository.get_revenue_by_period(start_date, end_date, group_by)
            
            # Prepare chart data
            labels = []
            data_points = []
            
            for item in revenue_data:
                period_str = item['period'].strftime('%Y-%m-%d' if group_by == 'day' else '%Y-%m-%d')
                labels.append(period_str)
                data_points.append(ChartDataPoint(
                    label=period_str,
                    value=Decimal(str(item['total_revenue'])),
                    date=item['period']
                ))
            
            datasets = [{
                'label': 'Revenue',
                'data': [float(dp.value) for dp in data_points],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2
            }]
            
            return ChartData(
                title=f"Revenue Trend ({days} days)",
                chart_type="line",
                data_points=data_points,
                labels=labels,
                datasets=datasets
            )
            
        except Exception as e:
            logger.error(f"Error getting revenue chart data: {e}")
            raise
    
    async def get_product_performance_chart(self, days: int = 30) -> ChartData:
        """Mendapatkan data chart performa produk"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            top_products = self.repository.get_top_products(start_date, end_date, limit=10)
            
            labels = [f"Product {p['product_id']}" for p in top_products]
            data_points = []
            
            for product in top_products:
                data_points.append(ChartDataPoint(
                    label=f"Product {product['product_id']}",
                    value=Decimal(str(product['total_revenue']))
                ))
            
            datasets = [{
                'label': 'Revenue by Product',
                'data': [float(dp.value) for dp in data_points],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 205, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(199, 199, 199, 0.2)',
                    'rgba(83, 102, 255, 0.2)',
                    'rgba(255, 99, 255, 0.2)',
                    'rgba(99, 255, 132, 0.2)'
                ],
                'borderWidth': 1
            }]
            
            return ChartData(
                title="Top Products by Revenue",
                chart_type="bar",
                data_points=data_points,
                labels=labels,
                datasets=datasets
            )
            
        except Exception as e:
            logger.error(f"Error getting product performance chart: {e}")
            raise
    
    async def get_voucher_usage_chart(self, days: int = 30) -> ChartData:
        """Mendapatkan data chart penggunaan voucher"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            top_vouchers = self.repository.get_top_vouchers(start_date, end_date, limit=10)
            
            labels = [f"Voucher {v['voucher_id']}" for v in top_vouchers]
            data_points = []
            
            for voucher in top_vouchers:
                data_points.append(ChartDataPoint(
                    label=f"Voucher {voucher['voucher_id']}",
                    value=Decimal(str(voucher['usage_count']))
                ))
            
            datasets = [{
                'label': 'Voucher Usage Count',
                'data': [float(dp.value) for dp in data_points],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 205, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(199, 199, 199, 0.6)',
                    'rgba(83, 102, 255, 0.6)',
                    'rgba(255, 99, 255, 0.6)',
                    'rgba(99, 255, 132, 0.6)'
                ]
            }]
            
            return ChartData(
                title="Top Vouchers by Usage",
                chart_type="pie",
                data_points=data_points,
                labels=labels,
                datasets=datasets
            )
            
        except Exception as e:
            logger.error(f"Error getting voucher usage chart: {e}")
            raise
    
    async def get_user_activity_chart(self, days: int = 30) -> ChartData:
        """Mendapatkan data chart aktivitas user"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get daily user activity
            daily_activity = []
            current_date = start_date
            
            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                
                filter_params = AnalyticsFilter(
                    start_date=current_date,
                    end_date=next_date,
                    event_type="user_login"
                )
                
                daily_logins = len(self.repository.get_events_by_filter(filter_params, limit=1000))
                
                daily_activity.append({
                    'date': current_date,
                    'logins': daily_logins
                })
                
                current_date = next_date
            
            labels = [item['date'].strftime('%Y-%m-%d') for item in daily_activity]
            data_points = []
            
            for item in daily_activity:
                data_points.append(ChartDataPoint(
                    label=item['date'].strftime('%Y-%m-%d'),
                    value=Decimal(str(item['logins'])),
                    date=item['date']
                ))
            
            datasets = [{
                'label': 'Daily Logins',
                'data': [float(dp.value) for dp in data_points],
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
                'fill': True
            }]
            
            return ChartData(
                title="User Activity Trend",
                chart_type="line",
                data_points=data_points,
                labels=labels,
                datasets=datasets
            )
            
        except Exception as e:
            logger.error(f"Error getting user activity chart: {e}")
            raise
    
    async def track_product_view(self, product_id: int, user_id: Optional[int] = None,
                                session_id: Optional[str] = None, ip_address: Optional[str] = None):
        """Helper method untuk track product view"""
        event_data = AnalyticsEventCreate(
            event_type="product_view",
            user_id=user_id,
            session_id=session_id,
            product_id=product_id,
            ip_address=ip_address
        )
        return await self.track_event(event_data)
    
    async def track_product_purchase(self, product_id: int, user_id: int, amount: Decimal,
                                   transaction_id: Optional[int] = None, session_id: Optional[str] = None):
        """Helper method untuk track product purchase"""
        event_data = AnalyticsEventCreate(
            event_type="product_purchase",
            user_id=user_id,
            session_id=session_id,
            product_id=product_id,
            transaction_id=transaction_id,
            amount=amount
        )
        return await self.track_event(event_data)
    
    async def track_voucher_usage(self, voucher_id: int, user_id: int, discount_amount: Decimal,
                                transaction_id: Optional[int] = None):
        """Helper method untuk track voucher usage"""
        event_data = AnalyticsEventCreate(
            event_type="voucher_used",
            user_id=user_id,
            voucher_id=voucher_id,
            transaction_id=transaction_id,
            amount=discount_amount
        )
        return await self.track_event(event_data)


# Create a factory function to get analytics service instance
def get_analytics_service(db: Session) -> AnalyticsService:
    """Factory function to create analytics service instance"""
    return AnalyticsService(db)


# For backward compatibility, create a default instance
class AnalyticsServiceSingleton:
    """Singleton wrapper for analytics service"""
    
    def get_dashboard_stats(self, db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get dashboard statistics"""
        service = AnalyticsService(db)
        try:
            # Return basic stats structure
            return {
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
        except Exception as e:
            logger.warning(f"Could not get dashboard stats: {e}")
            return {
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
    
    def get_recent_events(self, db: Session, limit: int = 100, event_type: str = None) -> List[Dict[str, Any]]:
        """Get recent events"""
        try:
            service = AnalyticsService(db)
            # Return empty list for now
            return []
        except Exception as e:
            logger.warning(f"Could not get recent events: {e}")
            return []
    
    def get_performance_metrics(self, db: Session) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            return {
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
        except Exception as e:
            logger.warning(f"Could not get performance metrics: {e}")
            return {
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


# Create singleton instance
analytics_service = AnalyticsServiceSingleton()
