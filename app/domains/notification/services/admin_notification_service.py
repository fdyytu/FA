from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import logging
import json

from app.models.notification import (
    AdminNotificationSetting, NotificationType, NotificationChannel
)
from app.models.admin import Admin
from app.schemas.notification import (
    AdminNotificationSettingCreate, AdminNotificationSettingUpdate,
    NotificationSendRequest
)
from app.utils.exceptions import HTTPException
from .notification_channel_service import NotificationChannelService

logger = logging.getLogger(__name__)

class AdminNotificationService:
    """Service untuk mengelola notifikasi admin - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
        self.channel_service = NotificationChannelService(db)
    
    async def send_admin_notification(self, request: NotificationSendRequest) -> Dict[str, bool]:
        """Kirim notifikasi ke admin berdasarkan pengaturan mereka"""
        try:
            # Ambil semua admin yang aktif
            active_admins = self.db.query(Admin).filter(Admin.is_active == True).all()
            
            results = {}
            
            for admin in active_admins:
                # Cek pengaturan notifikasi admin untuk tipe notifikasi ini
                settings = self.db.query(AdminNotificationSetting).filter(
                    and_(
                        AdminNotificationSetting.admin_id == admin.id,
                        AdminNotificationSetting.notification_type == request.notification_type,
                        AdminNotificationSetting.is_enabled == True
                    )
                ).all()
                
                # Jika tidak ada pengaturan khusus, gunakan channel default
                if not settings:
                    admin_results = await self.channel_service.send_notification(request)
                    results[f"admin_{admin.id}"] = admin_results
                else:
                    # Kirim hanya ke channel yang diaktifkan admin
                    enabled_channels = [setting.channel for setting in settings]
                    filtered_request = NotificationSendRequest(
                        title=request.title,
                        message=request.message,
                        notification_type=request.notification_type,
                        channels=[ch for ch in request.channels if ch in enabled_channels]
                    )
                    
                    if filtered_request.channels:
                        admin_results = await self.channel_service.send_notification(filtered_request)
                        results[f"admin_{admin.id}"] = admin_results
            
            logger.info(f"Admin notifications sent for type: {request.notification_type}")
            return results
            
        except Exception as e:
            logger.error(f"Error sending admin notifications: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengirim notifikasi admin: {str(e)}")
    
    async def get_admin_notification_settings(self, admin_id: int) -> List[AdminNotificationSetting]:
        """Ambil pengaturan notifikasi admin"""
        try:
            settings = self.db.query(AdminNotificationSetting).filter(
                AdminNotificationSetting.admin_id == admin_id
            ).all()
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting admin notification settings: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil pengaturan notifikasi: {str(e)}")
    
    async def update_admin_notification_setting(
        self, 
        admin_id: int, 
        notification_type: NotificationType,
        channel: NotificationChannel,
        setting_data: AdminNotificationSettingUpdate
    ) -> AdminNotificationSetting:
        """Update pengaturan notifikasi admin"""
        try:
            setting = self.db.query(AdminNotificationSetting).filter(
                and_(
                    AdminNotificationSetting.admin_id == admin_id,
                    AdminNotificationSetting.notification_type == notification_type,
                    AdminNotificationSetting.channel == channel
                )
            ).first()
            
            if not setting:
                raise HTTPException(status_code=404, detail="Pengaturan notifikasi tidak ditemukan")
            
            # Update fields
            update_data = setting_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(setting, field, value)
            
            setting.updated_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(setting)
            
            logger.info(f"Admin notification setting updated for admin {admin_id}")
            return setting
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating admin notification setting: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengupdate pengaturan notifikasi: {str(e)}")
    
    async def create_admin_notification_setting(self, setting_data: AdminNotificationSettingCreate) -> AdminNotificationSetting:
        """Buat pengaturan notifikasi admin baru"""
        try:
            # Cek apakah pengaturan sudah ada
            existing = self.db.query(AdminNotificationSetting).filter(
                and_(
                    AdminNotificationSetting.admin_id == setting_data.admin_id,
                    AdminNotificationSetting.notification_type == setting_data.notification_type,
                    AdminNotificationSetting.channel == setting_data.channel
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail="Pengaturan notifikasi untuk kombinasi ini sudah ada"
                )
            
            db_setting = AdminNotificationSetting(**setting_data.dict())
            
            self.db.add(db_setting)
            self.db.commit()
            self.db.refresh(db_setting)
            
            logger.info(f"Admin notification setting created for admin {setting_data.admin_id}")
            return db_setting
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating admin notification setting: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat pengaturan notifikasi: {str(e)}")
