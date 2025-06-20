"""
Test Notification Controller
Controller untuk endpoint testing notifikasi
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

try:
    from app.utils.responses import create_success_response, create_error_response
except ImportError:
    def create_success_response(data, message="Success"):
        return {"success": True, "data": data, "message": message}
    def create_error_response(message, status_code=400):
        return {"success": False, "message": message, "status_code": status_code}

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


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
        
        try:
            from app.services.notification_service import NotificationChannelService
        except ImportError:
            return create_error_response("NotificationChannelService not available", 503)
        
        service = NotificationChannelService(db)
        success = await service.send_email(email, subject, message)
        
        if success:
            return create_success_response(
                data={"sent": True, "email": email},
                message="Test email berhasil dikirim"
            )
        else:
            return create_error_response(message="Gagal kirim test email")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        return create_error_response(message=f"Gagal kirim test email: {str(e)}")


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
        
        try:
            from app.services.notification_service import NotificationChannelService
        except ImportError:
            return create_error_response("NotificationChannelService not available", 503)
        
        service = NotificationChannelService(db)
        success = await service.send_whatsapp(phone_number, message)
        
        if success:
            return create_success_response(
                data={"sent": True, "phone_number": phone_number},
                message="Test WhatsApp berhasil dikirim"
            )
        else:
            return create_error_response(message="Gagal kirim test WhatsApp")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending test WhatsApp: {str(e)}")
        return create_error_response(message=f"Gagal kirim test WhatsApp: {str(e)}")


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
        
        try:
            from app.services.notification_service import NotificationChannelService
        except ImportError:
            return create_error_response("NotificationChannelService not available", 503)
        
        service = NotificationChannelService(db)
        success = await service.send_discord(webhook_url, title, message)
        
        if success:
            return create_success_response(
                data={"sent": True, "webhook_url": webhook_url},
                message="Test Discord berhasil dikirim"
            )
        else:
            return create_error_response(message="Gagal kirim test Discord")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error sending test Discord: {str(e)}")
        return create_error_response(message=f"Gagal kirim test Discord: {str(e)}")
