"""
Admin Notification Controller
Controller untuk endpoint notifikasi admin
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.api.deps import get_db, get_current_user

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

# Try to import services
try:
    from app.domains.notification.services.notification_service import AdminNotificationService
except ImportError:
    AdminNotificationService = None

# Try to import schemas
try:
    from app.schemas.notification import (
        AdminNotificationSettingCreate, AdminNotificationSettingUpdate,
        NotificationSendRequest
    )
except ImportError:
    AdminNotificationSettingCreate = AdminNotificationSettingUpdate = None
    NotificationSendRequest = None

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


@router.post("/admin/send", response_model=dict)
async def send_admin_notification(
    request: NotificationSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send notifikasi dari admin ke user/group"""
    try:
        if not AdminNotificationService:
            return create_error_response("Admin notification service not available", 503)
        
        service = AdminNotificationService(db)
        result = await service.send_notification(
            sender_id=current_user.id,
            notification_data=request.dict()
        )
        
        return create_success_response(result, "Notification sent successfully")
        
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
        return create_error_response("Failed to send notification", 500)


@router.post("/admin/settings", response_model=dict)
async def create_admin_notification_setting(
    request: AdminNotificationSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Buat pengaturan notifikasi admin baru"""
    try:
        if not AdminNotificationService:
            return create_error_response("Admin notification service not available", 503)
        
        service = AdminNotificationService(db)
        setting = await service.create_notification_setting(
            admin_id=current_user.id,
            setting_data=request.dict()
        )
        
        return create_success_response(setting, "Notification setting created successfully")
        
    except Exception as e:
        logger.error(f"Error creating admin notification setting: {e}")
        return create_error_response("Failed to create notification setting", 500)
