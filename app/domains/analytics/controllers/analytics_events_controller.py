from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.domains.analytics.services.analytics_service import AnalyticsService
from app.domains.analytics.schemas.analytics_schemas import (
    AnalyticsEventCreate, AnalyticsFilter
)
from app.core.database import get_db
from app.common.responses.api_response import create_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Dependency untuk mendapatkan AnalyticsService"""
    return AnalyticsService(db)

@router.post("/events", response_model=dict, summary="Track Analytics Event")
async def track_event(
    event_data: AnalyticsEventCreate,
    request: Request,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Track event analytics baru.
    
    - **event_type**: Tipe event (product_view, product_purchase, etc.)
    - **user_id**: ID user (optional)
    - **product_id**: ID produk (optional)
    - **amount**: Jumlah uang terkait (optional)
    """
    try:
        # Auto-populate IP address if not provided
        if not event_data.ip_address:
            event_data.ip_address = request.client.host
        
        # Auto-populate user agent if not provided
        if not event_data.user_agent:
            event_data.user_agent = request.headers.get("user-agent")
        
        event = await service.track_event(event_data)
        
        return create_response(
            success=True,
            message="Event analytics berhasil ditrack",
            data={"event_id": event.id, "event_type": event.event_type}
        )
        
    except Exception as e:
        logger.error(f"Error tracking analytics event: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking event")

@router.get("/events", response_model=dict, summary="Get Analytics Events")
async def get_events(
    start_date: Optional[datetime] = Query(None, description="Tanggal mulai filter"),
    end_date: Optional[datetime] = Query(None, description="Tanggal akhir filter"),
    event_type: Optional[str] = Query(None, description="Filter berdasarkan tipe event"),
    user_id: Optional[int] = Query(None, description="Filter berdasarkan user ID"),
    product_id: Optional[int] = Query(None, description="Filter berdasarkan product ID"),
    voucher_id: Optional[int] = Query(None, description="Filter berdasarkan voucher ID"),
    limit: int = Query(100, ge=1, le=1000, description="Jumlah maksimal data"),
    offset: int = Query(0, ge=0, description="Offset untuk pagination"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Mendapatkan daftar events analytics berdasarkan filter.
    
    Mendukung filtering berdasarkan:
    - Tanggal (start_date, end_date)
    - Tipe event
    - User ID
    - Product ID
    - Voucher ID
    """
    try:
        filter_params = AnalyticsFilter(
            start_date=start_date,
            end_date=end_date,
            event_type=event_type,
            user_id=user_id,
            product_id=product_id,
            voucher_id=voucher_id
        )
        
        events = await service.get_events(filter_params, limit, offset)
        
        # Convert to response format
        events_data = []
        for event in events:
            events_data.append({
                "id": event.id,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "product_id": event.product_id,
                "voucher_id": event.voucher_id,
                "amount": float(event.amount) if event.amount else None,
                "event_timestamp": event.event_timestamp.isoformat(),
                "ip_address": event.ip_address
            })
        
        return create_response(
            success=True,
            message="Data events analytics berhasil diambil",
            data={
                "events": events_data,
                "total": len(events_data),
                "limit": limit,
                "offset": offset
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics events: {e}")
        raise HTTPException(status_code=500, detail="Gagal mengambil data events")
