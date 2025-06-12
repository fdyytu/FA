from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.domains.user.services.user_settings_service import UserSettingsService
from app.domains.user.services.user_security_service import UserSecurityService
from app.schemas.user_profile import (
    UserSettingsUpdate, UserPasswordChange, UserSecuritySettings,
    UserActivityLog, UserPreferences
)
from app.utils.responses import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/settings", response_model=dict)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan pengaturan user"""
    try:
        service = UserSettingsService(db)
        settings = await service.get_user_settings(current_user.id)
        
        return create_success_response(
            data=settings.dict() if settings else None,
            message="Pengaturan berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user settings: {str(e)}")
        return create_error_response(message=f"Gagal mengambil pengaturan: {str(e)}")

@router.put("/settings", response_model=dict)
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update pengaturan user"""
    try:
        service = UserSettingsService(db)
        settings = await service.update_user_settings(current_user.id, settings_data)
        
        return create_success_response(
            data=settings.dict(),
            message="Pengaturan berhasil diupdate"
        )
        
    except Exception as e:
        logger.error(f"Error updating user settings: {str(e)}")
        return create_error_response(message=f"Gagal update pengaturan: {str(e)}")

@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ganti password user"""
    try:
        service = UserSecurityService(db)
        await service.change_password(current_user.id, password_data)
        
        return create_success_response(
            data=None,
            message="Password berhasil diubah"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return create_error_response(message=f"Gagal mengubah password: {str(e)}")

@router.get("/security", response_model=dict)
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan pengaturan keamanan user"""
    try:
        service = UserSecurityService(db)
        security_settings = await service.get_security_settings(current_user.id)
        
        return create_success_response(
            data=security_settings.dict(),
            message="Pengaturan keamanan berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting security settings: {str(e)}")
        return create_error_response(message=f"Gagal mengambil pengaturan keamanan: {str(e)}")

@router.post("/enable-2fa", response_model=dict)
async def enable_two_factor_auth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktifkan 2FA untuk user"""
    try:
        service = UserSecurityService(db)
        qr_code_url = await service.enable_2fa(current_user.id)
        
        return create_success_response(
            data={"qr_code_url": qr_code_url},
            message="2FA berhasil diaktifkan. Scan QR code dengan aplikasi authenticator"
        )
        
    except Exception as e:
        logger.error(f"Error enabling 2FA: {str(e)}")
        return create_error_response(message=f"Gagal mengaktifkan 2FA: {str(e)}")

@router.post("/disable-2fa", response_model=dict)
async def disable_two_factor_auth(
    verification_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Nonaktifkan 2FA untuk user"""
    try:
        service = UserSecurityService(db)
        await service.disable_2fa(current_user.id, verification_code)
        
        return create_success_response(
            data=None,
            message="2FA berhasil dinonaktifkan"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error disabling 2FA: {str(e)}")
        return create_error_response(message=f"Gagal menonaktifkan 2FA: {str(e)}")

@router.get("/activity-logs", response_model=dict)
async def get_activity_logs(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan log aktivitas user"""
    try:
        service = UserSettingsService(db)
        logs = await service.get_activity_logs(current_user.id, page, limit)
        
        return create_success_response(
            data={
                "logs": [log.dict() for log in logs],
                "page": page,
                "limit": limit
            },
            message="Log aktivitas berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting activity logs: {str(e)}")
        return create_error_response(message=f"Gagal mengambil log aktivitas: {str(e)}")

@router.get("/preferences", response_model=dict)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan preferensi user"""
    try:
        service = UserSettingsService(db)
        preferences = await service.get_user_preferences(current_user.id)
        
        return create_success_response(
            data=preferences.dict() if preferences else None,
            message="Preferensi berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        return create_error_response(message=f"Gagal mengambil preferensi: {str(e)}")

@router.put("/preferences", response_model=dict)
async def update_user_preferences(
    preferences_data: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update preferensi user"""
    try:
        service = UserSettingsService(db)
        preferences = await service.update_user_preferences(current_user.id, preferences_data)
        
        return create_success_response(
            data=preferences.dict(),
            message="Preferensi berhasil diupdate"
        )
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        return create_error_response(message=f"Gagal update preferensi: {str(e)}")
