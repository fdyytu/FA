from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
from app.models.notification import (
    Notification, NotificationType, NotificationChannel, NotificationStatus
)
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse
)
from app.utils.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service untuk mengelola notifikasi - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """Membuat notifikasi baru"""
        try:
            db_notification = Notification(**notification_data.dict())
            
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)
            
            logger.info(f"Notifikasi berhasil dibuat: {db_notification.id}")
            return NotificationResponse.from_orm(db_notification)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat notifikasi: {str(e)}")
    
    async def get_user_notifications(self, user_id: int, page: int = 1, limit: int = 10) -> List[NotificationResponse]:
        """Mendapatkan notifikasi user"""
        try:
            offset = (page - 1) * limit
            notifications = self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
            
            return [NotificationResponse.from_orm(n) for n in notifications]
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil notifikasi: {str(e)}")
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> NotificationResponse:
        """Tandai notifikasi sebagai sudah dibaca"""
        try:
            notification = self.db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if not notification:
                raise HTTPException(status_code=404, detail="Notifikasi tidak ditemukan")
            
            notification.is_read = True
            notification.read_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(notification)
            
            return NotificationResponse.from_orm(notification)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking notification as read: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal menandai notifikasi: {str(e)}")
