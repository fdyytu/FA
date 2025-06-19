from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.domains.analytics.services.analytics_service import AnalyticsService
from app.domains.analytics.schemas.analytics_schemas import AnalyticsEventCreate
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

@router.post("/track/product-view", summary="Track Product View")
async def track_product_view(
    product_id: int,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    request: Request = None,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Helper endpoint untuk track product view"""
    try:
        ip_address = request.client.host if request else None
        await service.track_product_view(product_id, user_id, session_id, ip_address)
        
        return create_response(
            success=True,
            message="Product view berhasil ditrack"
        )
    except Exception as e:
        logger.error(f"Error tracking product view: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking")

@router.post("/track/product-purchase", summary="Track Product Purchase")
async def track_product_purchase(
    product_id: int,
    user_id: int,
    amount: float,
    transaction_id: Optional[int] = None,
    session_id: Optional[str] = None,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Helper endpoint untuk track product purchase"""
    try:
        await service.track_product_purchase(
            product_id, user_id, Decimal(str(amount)), transaction_id, session_id
        )
        
        return create_response(
            success=True,
            message="Product purchase berhasil ditrack"
        )
    except Exception as e:
        logger.error(f"Error tracking product purchase: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking")

@router.post("/track/voucher-usage", summary="Track Voucher Usage")
async def track_voucher_usage(
    voucher_id: int,
    user_id: int,
    discount_amount: float,
    transaction_id: Optional[int] = None,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Helper endpoint untuk track voucher usage"""
    try:
        await service.track_voucher_usage(
            voucher_id, user_id, Decimal(str(discount_amount)), transaction_id
        )
        
        return create_response(
            success=True,
            message="Voucher usage berhasil ditrack"
        )
    except Exception as e:
        logger.error(f"Error tracking voucher usage: {e}")
        raise HTTPException(status_code=500, detail="Gagal melakukan tracking")
