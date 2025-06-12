from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.notification_service import (
    NotificationService, AdminNotificationService, WebhookService
)
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    AdminNotificationSettingCreate, AdminNotificationSettingUpdate,
    NotificationSendRequest, WebhookLogCreate
)
from app.utils.responses import success_response, error_response
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# Endpoints untuk notifikasi user
@router.get("/", response_model=dict)
async def get_user_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan notifikasi user"""
    try:
        service = NotificationService(db)
        notifications = await service.get_user_notifications(current_user.id, page, limit)
        
        return success_response(
            data={
                "notifications": [n.dict() for n in notifications],
                "page": page,
                "limit": limit,
                "total": len(notifications)
            },
            message="Notifikasi berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        return error_response(message=f"Gagal mengambil notifikasi: {str(e)}")

@router.post("/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tandai notifikasi sebagai sudah dibaca"""
    try:
        service = NotificationService(db)
        notification = await service.mark_as_read(notification_id, current_user.id)
        
        return success_response(
            data=notification.dict(),
            message="Notifikasi berhasil ditandai sebagai dibaca"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return error_response(message=f"Gagal menandai notifikasi: {str(e)}")

# Endpoints untuk admin notifikasi
@router.post("/admin/send", response_model=dict)
async def send_admin_notification(
    notification_request: NotificationSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kirim notifikasi ke admin (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = AdminNotificationService(db)
        await service.send_admin_notification(notification_request)
        
        return success_response(
            data=None,
            message="Notifikasi admin berhasil dikirim"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")
        return error_response(message=f"Gagal kirim notifikasi admin: {str(e)}")

@router.post("/admin/settings", response_model=dict)
async def create_admin_notification_setting(
    setting_data: AdminNotificationSettingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buat pengaturan notifikasi admin (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = AdminNotificationService(db)
        setting = await service.create_admin_notification_setting(setting_data)
        
        return success_response(
            data={
                "id": setting.id,
                "admin_id": setting.admin_id,
                "notification_type": setting.notification_type.value,
                "channel": setting.channel.value,
                "is_enabled": setting.is_enabled
            },
            message="Pengaturan notifikasi admin berhasil dibuat"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating admin notification setting: {str(e)}")
        return error_response(message=f"Gagal membuat pengaturan notifikasi: {str(e)}")

# Webhook endpoints
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
        log_data = WebhookLogCreate(
            webhook_type="digiflazz",
            request_method=request.method,
            request_url=str(request.url),
            request_headers=json.dumps(headers),
            request_body=json.dumps(webhook_data),
            processed=False
        )
        
        service = WebhookService(db)
        
        # Proses webhook
        success = await service.process_digiflazz_webhook(webhook_data)
        
        if success:
            return success_response(
                data={"processed": True},
                message="Webhook berhasil diproses"
            )
        else:
            return error_response(
                message="Gagal memproses webhook",
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"Error processing Digiflazz webhook: {str(e)}")
        return error_response(
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
        
        from app.models.notification import WebhookLog
        
        query = db.query(WebhookLog)
        
        if webhook_type:
            query = query.filter(WebhookLog.webhook_type == webhook_type)
        
        if processed is not None:
            query = query.filter(WebhookLog.processed == processed)
        
        offset = (page - 1) * limit
        logs = query.order_by(WebhookLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return success_response(
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
        return error_response(message=f"Gagal mengambil log webhook: {str(e)}")

# Test endpoints untuk notifikasi
@router.post("/test/email", response_model=dict)
async def test_email_notification(
    email: str,
    subject: str = "Test Email",
    message: str = "Ini adalah test email dari sistem FA",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test kirim email (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        from app.services.notification_service import NotificationChannelService
        
        service = NotificationChannelService(db)
        success = await service.send_email(email, subject, message)
        
        if success:
            return success_response(
                data={"sent": True, "email": email},
                message="Test email berhasil dikirim"
            )
        else:
            return error_response(message="Gagal kirim test email")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return error_response(message=f"Gagal kirim test email: {str(e)}")

@router.post("/test/whatsapp", response_model=dict)
async def test_whatsapp_notification(
    phone_number: str,
    message: str = "Ini adalah test WhatsApp dari sistem FA",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test kirim WhatsApp (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        from app.services.notification_service import NotificationChannelService
        
        service = NotificationChannelService(db)
        success = await service.send_whatsapp(phone_number, message)
        
        if success:
            return success_response(
                data={"sent": True, "phone_number": phone_number},
                message="Test WhatsApp berhasil dikirim"
            )
        else:
            return error_response(message="Gagal kirim test WhatsApp")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending test WhatsApp: {str(e)}")
        return error_response(message=f"Gagal kirim test WhatsApp: {str(e)}")

@router.post("/test/discord", response_model=dict)
async def test_discord_notification(
    webhook_url: str,
    title: str = "Test Discord",
    message: str = "Ini adalah test Discord dari sistem FA",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test kirim Discord (admin only)"""
    try:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        from app.services.notification_service import NotificationChannelService
        
        service = NotificationChannelService(db)
        success = await service.send_discord(webhook_url, title, message)
        
        if success:
            return success_response(
                data={"sent": True, "webhook_url": webhook_url},
                message="Test Discord berhasil dikirim"
            )
        else:
            return error_response(message="Gagal kirim test Discord")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending test Discord: {str(e)}")
        return error_response(message=f"Gagal kirim test Discord: {str(e)}")
