from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.user import User
from app.schemas.user_profile import (
    UserSettingsUpdate, UserPreferences, UserActivityLog
)
from app.utils.exceptions import HTTPException
from app.shared.base_classes.base_service import BaseService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserSettingsService(BaseService):
    """Service untuk mengelola pengaturan dan preferensi user"""
    
    def __init__(self, db: Session):
        super().__init__(db)
    
    async def get_user_settings(self, user_id: int) -> Optional[dict]:
        """Mendapatkan pengaturan user"""
        try:
            # Untuk saat ini, kita akan menggunakan data default
            # Nantinya bisa dipindah ke tabel terpisah untuk user settings
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            settings = {
                "notifications": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "transaction_alerts": True,
                    "marketing_emails": False
                },
                "privacy": {
                    "profile_visibility": "public",
                    "show_balance": False,
                    "show_transaction_history": False
                },
                "security": {
                    "two_factor_enabled": False,
                    "login_alerts": True,
                    "session_timeout": 30
                },
                "display": {
                    "language": "id",
                    "timezone": "Asia/Jakarta",
                    "currency": "IDR",
                    "theme": "light"
                }
            }
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil pengaturan: {str(e)}")
    
    async def update_user_settings(self, user_id: int, settings_data: UserSettingsUpdate) -> dict:
        """Update pengaturan user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Untuk implementasi sederhana, kita akan menyimpan di field JSON atau tabel terpisah
            # Saat ini return data yang diupdate
            updated_settings = settings_data.dict(exclude_unset=True)
            
            # Log aktivitas
            await self._log_user_activity(
                user_id, 
                "settings_updated", 
                f"User mengupdate pengaturan: {list(updated_settings.keys())}"
            )
            
            logger.info(f"Pengaturan user berhasil diupdate untuk user_id: {user_id}")
            return updated_settings
            
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal update pengaturan: {str(e)}")
    
    async def get_user_preferences(self, user_id: int) -> Optional[dict]:
        """Mendapatkan preferensi user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            # Default preferences
            preferences = {
                "dashboard": {
                    "show_balance": True,
                    "show_recent_transactions": True,
                    "show_quick_actions": True,
                    "default_view": "overview"
                },
                "transactions": {
                    "default_amount": 0,
                    "favorite_providers": [],
                    "auto_save_recipients": True
                },
                "notifications": {
                    "transaction_success": True,
                    "low_balance_alert": True,
                    "promotional_offers": False
                }
            }
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil preferensi: {str(e)}")
    
    async def update_user_preferences(self, user_id: int, preferences_data: UserPreferences) -> dict:
        """Update preferensi user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User tidak ditemukan")
            
            updated_preferences = preferences_data.dict(exclude_unset=True)
            
            # Log aktivitas
            await self._log_user_activity(
                user_id, 
                "preferences_updated", 
                f"User mengupdate preferensi: {list(updated_preferences.keys())}"
            )
            
            logger.info(f"Preferensi user berhasil diupdate untuk user_id: {user_id}")
            return updated_preferences
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal update preferensi: {str(e)}")
    
    async def get_activity_logs(self, user_id: int, page: int = 1, limit: int = 20) -> List[dict]:
        """Mendapatkan log aktivitas user"""
        try:
            # Untuk implementasi sederhana, kita akan return data dummy
            # Nantinya bisa menggunakan tabel user_activity_logs
            
            # Simulasi data log aktivitas
            activities = [
                {
                    "id": 1,
                    "activity_type": "login",
                    "description": "User login ke aplikasi",
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                    "created_at": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "activity_type": "profile_updated",
                    "description": "User mengupdate profil",
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            # Pagination simulation
            start = (page - 1) * limit
            end = start + limit
            
            return activities[start:end]
            
        except Exception as e:
            logger.error(f"Error getting activity logs: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil log aktivitas: {str(e)}")
    
    async def _log_user_activity(self, user_id: int, activity_type: str, description: str) -> None:
        """Log aktivitas user (helper method)"""
        try:
            # Implementasi logging aktivitas user
            # Bisa disimpan ke tabel user_activity_logs
            logger.info(f"User Activity - user_id: {user_id}, type: {activity_type}, desc: {description}")
            
        except Exception as e:
            logger.error(f"Error logging user activity: {str(e)}")
            # Jangan raise exception untuk logging, agar tidak mengganggu flow utama
