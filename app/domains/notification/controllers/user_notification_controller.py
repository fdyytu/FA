"""
User Notification Controller
Controller untuk endpoint notifikasi user
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.api.deps import get_db, get_current_user

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

# Try to import services
try:
    from app.domains.notification.services.notification_service import NotificationService
except ImportError:
    NotificationService = None

# Try to import schemas
try:
    from app.schemas.notification import NotificationResponse
except ImportError:
    NotificationResponse = None

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


@router.get("/", response_model=dict)
async def get_user_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ambil notifikasi user dengan pagination"""
    try:
        if not NotificationService:
            return create_error_response("Notification service not available", 503)
        
        service = NotificationService(db)
        notifications, total = await service.get_user_notifications(
            user_id=current_user.id,
            page=page,
            limit=limit,
            unread_only=unread_only
        )
        
        return create_success_response({
            "notifications": notifications,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {e}")
        return create_error_response("Failed to get notifications", 500)


@router.post("/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark notifikasi sebagai sudah dibaca"""
    try:
        if not NotificationService:
            return create_error_response("Notification service not available", 503)
        
        service = NotificationService(db)
        success = await service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user.id
        )
        
        if success:
            return create_success_response(None, "Notification marked as read")
        else:
            return create_error_response("Notification not found or already read", 404)
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return create_error_response("Failed to mark notification as read", 500)
