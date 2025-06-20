"""
Webhook Notification Controller
Controller untuk endpoint webhook notifikasi
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.api.deps import get_db, get_current_user

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

# Try to import services
try:
    from app.domains.notification.services.notification_service import WebhookService
except ImportError:
    WebhookService = None

# Try to import schemas
try:
    from app.schemas.notification import WebhookLogCreate
except ImportError:
    WebhookLogCreate = None

try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/digiflazz", response_model=dict)
async def digiflazz_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Webhook endpoint untuk Digiflazz"""
    try:
        # Ambil data dari request
        webhook_data = await request.json()
        
        # Log request headers
        headers = dict(request.headers)
        
        # Log webhook
        if WebhookLogCreate:
            log_data = WebhookLogCreate(
                webhook_type="digiflazz",
                request_method=request.method,
                request_url=str(request.url),
                request_headers=json.dumps(headers),
                request_body=json.dumps(webhook_data),
                processed=False
            )
        
        if not WebhookService:
            return create_error_response("Webhook service not available", 503)
        
        service = WebhookService(db)
        
        # Proses webhook
        success = await service.process_digiflazz_webhook(webhook_data)
        
        if success:
            return create_success_response(
                data={"processed": True},
                message="Webhook berhasil diproses"
            )
        else:
            return create_error_response(
                message="Gagal memproses webhook",
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"Error processing Digiflazz webhook: {str(e)}")
        return create_error_response(
            message=f"Error webhook: {str(e)}",
            status_code=500
        )


@router.get("/webhook/logs", response_model=dict)
async def get_webhook_logs(
    webhook_type: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan log webhook (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        try:
            from app.models.notification import WebhookLog
        except ImportError:
            return create_error_response("WebhookLog model not available", 503)
        
        query = db.query(WebhookLog)
        
        if webhook_type:
            query = query.filter(WebhookLog.webhook_type == webhook_type)
        
        if processed is not None:
            query = query.filter(WebhookLog.processed == processed)
        
        offset = (page - 1) * limit
        logs = query.order_by(WebhookLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return create_success_response(
            data={
                "logs": [
                    {
                        "id": log.id,
                        "webhook_type": log.webhook_type,
                        "request_method": log.request_method,
                        "request_url": log.request_url,
                        "response_status": log.response_status,
                        "processed": log.processed,
                        "error_message": log.error_message,
                        "created_at": log.created_at
                    } for log in logs
                ],
                "page": page,
                "limit": limit,
                "total": len(logs)
            },
            message="Log webhook berhasil diambil"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting webhook logs: {str(e)}")
        return create_error_response(message=f"Gagal mengambil log webhook: {str(e)}")
