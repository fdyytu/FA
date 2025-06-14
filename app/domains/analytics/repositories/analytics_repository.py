from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
from app.domains.analytics.models.analytics import (
    AnalyticsEvent, ProductAnalytics, VoucherAnalytics, DashboardMetrics
)
from app.domains.analytics.schemas.analytics_schemas import AnalyticsEventCreate, AnalyticsFilter
from app.shared.base_classes.base_repository import BaseRepository
import json
import logging

logger = logging.getLogger(__name__)

class AnalyticsRepository(BaseRepository[AnalyticsEvent]):
    """
    Repository untuk menangani operasi database analytics.
    Mengimplementasikan Repository Pattern untuk abstraksi data access.
    """
    
    def __init__(self, db: Session):
        super().__init__(AnalyticsEvent, db)
    
    def create_event(self, event_data: AnalyticsEventCreate) -> AnalyticsEvent:
        """Membuat event analytics baru"""
        try:
            # Convert event_data dict to JSON string if exists
            event_data_json = None
            if event_data.event_data:
                event_data_json = json.dumps(event_data.event_data)
            
            db_event = AnalyticsEvent(
                event_type=event_data.event_type,
                user_id=event_data.user_id,
                session_id=event_data.session_id,
                product_id=event_data.product_id,
                voucher_id=event_data.voucher_id,
                transaction_id=event_data.transaction_id,
                event_data=event_data_json,
                amount=event_data.amount,
                ip_address=event_data.ip_address,
                user_agent=event_data.user_agent,
                referrer=event_data.referrer
            )
            
            self.db.add(db_event)
            self.db.commit()
            self.db.refresh(db_event)
            
            logger.info(f"Analytics event created: {event_data.event_type}")
            return db_event
            
        except Exception as e:
            logger.error(f"Error creating analytics event: {e}")
            self.db.rollback()
            raise
    
    def get_events_by_filter(self, filter_params: AnalyticsFilter, 
                           limit: int = 100, offset: int = 0) -> List[AnalyticsEvent]:
        """Mendapatkan events berdasarkan filter"""
        try:
            query = self.db.query(AnalyticsEvent)
            
            # Apply filters
            if filter_params.start_date:
                query = query.filter(AnalyticsEvent.event_timestamp >= filter_params.start_date)
            
            if filter_params.end_date:
                query = query.filter(AnalyticsEvent.event_timestamp <= filter_params.end_date)
            
            if filter_params.event_type:
                query = query.filter(AnalyticsEvent.event_type == filter_params.event_type)
            
            if filter_params.user_id:
                query = query.filter(AnalyticsEvent.user_id == filter_params.user_id)
            
            if filter_params.product_id:
                query = query.filter(AnalyticsEvent.product_id == filter_params.product_id)
            
            if filter_params.voucher_id:
                query = query.filter(AnalyticsEvent.voucher_id == filter_params.voucher_id)
            
            # Order by timestamp descending
            query = query.order_by(desc(AnalyticsEvent.event_timestamp))
            
            # Apply pagination
            return query.offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting events by filter: {e}")
            raise
    
    def get_product_analytics(self, start_date: datetime, end_date: datetime,
                            product_id: Optional[int] = None) -> List[ProductAnalytics]:
        """Mendapatkan analytics produk"""
        try:
            query = self.db.query(ProductAnalytics).filter(
                and_(
                    ProductAnalytics.date >= start_date,
                    ProductAnalytics.date <= end_date
                )
            )
            
            if product_id:
                query = query.filter(ProductAnalytics.product_id == product_id)
            
            return query.order_by(desc(ProductAnalytics.date)).all()
            
        except Exception as e:
            logger.error(f"Error getting product analytics: {e}")
            raise
    
    def get_voucher_analytics(self, start_date: datetime, end_date: datetime,
                            voucher_id: Optional[int] = None) -> List[VoucherAnalytics]:
        """Mendapatkan analytics voucher"""
        try:
            query = self.db.query(VoucherAnalytics).filter(
                and_(
                    VoucherAnalytics.date >= start_date,
                    VoucherAnalytics.date <= end_date
                )
            )
            
            if voucher_id:
                query = query.filter(VoucherAnalytics.voucher_id == voucher_id)
            
            return query.order_by(desc(VoucherAnalytics.date)).all()
            
        except Exception as e:
            logger.error(f"Error getting voucher analytics: {e}")
            raise
    
    def get_dashboard_metrics(self, metric_type: str = "daily", 
                            limit: int = 30) -> List[DashboardMetrics]:
        """Mendapatkan metrics untuk dashboard"""
        try:
            return self.db.query(DashboardMetrics).filter(
                DashboardMetrics.metric_type == metric_type
            ).order_by(desc(DashboardMetrics.date)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {e}")
            raise
    
    def get_revenue_by_period(self, start_date: datetime, end_date: datetime,
                            group_by: str = "day") -> List[Dict[str, Any]]:
        """Mendapatkan revenue berdasarkan periode"""
        try:
            if group_by == "day":
                date_trunc = func.date_trunc('day', AnalyticsEvent.event_timestamp)
            elif group_by == "week":
                date_trunc = func.date_trunc('week', AnalyticsEvent.event_timestamp)
            elif group_by == "month":
                date_trunc = func.date_trunc('month', AnalyticsEvent.event_timestamp)
            else:
                date_trunc = func.date_trunc('day', AnalyticsEvent.event_timestamp)
            
            result = self.db.query(
                date_trunc.label('period'),
                func.sum(AnalyticsEvent.amount).label('total_revenue'),
                func.count(AnalyticsEvent.id).label('transaction_count')
            ).filter(
                and_(
                    AnalyticsEvent.event_timestamp >= start_date,
                    AnalyticsEvent.event_timestamp <= end_date,
                    AnalyticsEvent.event_type.in_(['transaction_success', 'product_purchase']),
                    AnalyticsEvent.amount.isnot(None)
                )
            ).group_by(date_trunc).order_by(date_trunc).all()
            
            return [
                {
                    'period': row.period,
                    'total_revenue': float(row.total_revenue or 0),
                    'transaction_count': row.transaction_count
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting revenue by period: {e}")
            raise
    
    def get_top_products(self, start_date: datetime, end_date: datetime,
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Mendapatkan produk terpopuler"""
        try:
            result = self.db.query(
                AnalyticsEvent.product_id,
                func.count(AnalyticsEvent.id).label('view_count'),
                func.sum(
                    func.case(
                        (AnalyticsEvent.event_type == 'product_purchase', 1),
                        else_=0
                    )
                ).label('purchase_count'),
                func.sum(
                    func.case(
                        (AnalyticsEvent.event_type == 'product_purchase', AnalyticsEvent.amount),
                        else_=0
                    )
                ).label('total_revenue')
            ).filter(
                and_(
                    AnalyticsEvent.event_timestamp >= start_date,
                    AnalyticsEvent.event_timestamp <= end_date,
                    AnalyticsEvent.product_id.isnot(None),
                    AnalyticsEvent.event_type.in_(['product_view', 'product_purchase'])
                )
            ).group_by(AnalyticsEvent.product_id).order_by(
                desc('view_count')
            ).limit(limit).all()
            
            return [
                {
                    'product_id': row.product_id,
                    'view_count': row.view_count,
                    'purchase_count': row.purchase_count,
                    'total_revenue': float(row.total_revenue or 0),
                    'conversion_rate': (row.purchase_count / row.view_count * 100) if row.view_count > 0 else 0
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            raise
    
    def get_top_vouchers(self, start_date: datetime, end_date: datetime,
                        limit: int = 10) -> List[Dict[str, Any]]:
        """Mendapatkan voucher terpopuler"""
        try:
            result = self.db.query(
                AnalyticsEvent.voucher_id,
                func.count(AnalyticsEvent.id).label('usage_count'),
                func.sum(AnalyticsEvent.amount).label('total_discount')
            ).filter(
                and_(
                    AnalyticsEvent.event_timestamp >= start_date,
                    AnalyticsEvent.event_timestamp <= end_date,
                    AnalyticsEvent.voucher_id.isnot(None),
                    AnalyticsEvent.event_type == 'voucher_used'
                )
            ).group_by(AnalyticsEvent.voucher_id).order_by(
                desc('usage_count')
            ).limit(limit).all()
            
            return [
                {
                    'voucher_id': row.voucher_id,
                    'usage_count': row.usage_count,
                    'total_discount': float(row.total_discount or 0)
                }
                for row in result
            ]
            
        except Exception as e:
            logger.error(f"Error getting top vouchers: {e}")
            raise
    
    def get_user_activity_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Mendapatkan statistik aktivitas user"""
        try:
            # Total unique users
            unique_users = self.db.query(
                func.count(func.distinct(AnalyticsEvent.user_id))
            ).filter(
                and_(
                    AnalyticsEvent.event_timestamp >= start_date,
                    AnalyticsEvent.event_timestamp <= end_date,
                    AnalyticsEvent.user_id.isnot(None)
                )
            ).scalar()
            
            # New registrations
            new_registrations = self.db.query(
                func.count(AnalyticsEvent.id)
            ).filter(
                and_(
                    AnalyticsEvent.event_timestamp >= start_date,
                    AnalyticsEvent.event_timestamp <= end_date,
                    AnalyticsEvent.event_type == 'user_registration'
                )
            ).scalar()
            
            # Total logins
            total_logins = self.db.query(
                func.count(AnalyticsEvent.id)
            ).filter(
                and_(
                    AnalyticsEvent.event_timestamp >= start_date,
                    AnalyticsEvent.event_timestamp <= end_date,
                    AnalyticsEvent.event_type == 'user_login'
                )
            ).scalar()
            
            return {
                'unique_users': unique_users or 0,
                'new_registrations': new_registrations or 0,
                'total_logins': total_logins or 0,
                'avg_sessions_per_user': (total_logins / unique_users) if unique_users > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity stats: {e}")
            raise
