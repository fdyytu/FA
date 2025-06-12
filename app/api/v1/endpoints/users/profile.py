from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.domains.user.services.user_profile_service import UserProfileService
from app.domains.user.services.user_settings_service import UserSettingsService
from app.schemas.user_profile import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserDetailResponse, UserSettingsUpdate, UserPasswordChange
)
from app.utils.responses import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/profile", response_model=dict)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan profil user saat ini"""
    try:
        service = UserProfileService(db)
        profile = await service.get_profile(current_user.id)
        
        return create_success_response(
            data=profile.dict() if profile else None,
            message="Profil berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return create_error_response(message=f"Gagal mengambil profil: {str(e)}")

@router.post("/profile", response_model=dict)
async def create_my_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Membuat profil user baru"""
    try:
        service = UserProfileService(db)
        profile = await service.create_profile(current_user.id, profile_data)
        
        return create_success_response(
            data=profile.dict(),
            message="Profil berhasil dibuat"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        return create_error_response(message=f"Gagal membuat profil: {str(e)}")

@router.put("/profile", response_model=dict)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profil user"""
    try:
        service = UserProfileService(db)
        profile = await service.update_profile(current_user.id, profile_data)
        
        return create_success_response(
            data=profile.dict(),
            message="Profil berhasil diupdate"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        return create_error_response(message=f"Gagal update profil: {str(e)}")

@router.get("/detail", response_model=dict)
async def get_my_detail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan detail user lengkap dengan profil"""
    try:
        service = UserProfileService(db)
        user_detail = await service.get_user_detail(current_user.id)
        
        return create_success_response(
            data=user_detail.dict(),
            message="Detail user berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user detail: {str(e)}")
        return create_error_response(message=f"Gagal mengambil detail user: {str(e)}")

@router.post("/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload avatar user"""
    try:
        service = UserProfileService(db)
        avatar_url = await service.upload_avatar(current_user.id, file)
        
        return create_success_response(
            data={"avatar_url": avatar_url},
            message="Avatar berhasil diupload"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading avatar: {str(e)}")
        return create_error_response(message=f"Gagal upload avatar: {str(e)}")

@router.delete("/avatar", response_model=dict)
async def delete_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Hapus avatar user"""
    try:
        service = UserProfileService(db)
        await service.delete_avatar(current_user.id)
        
        return create_success_response(
            data=None,
            message="Avatar berhasil dihapus"
        )
        
    except Exception as e:
        logger.error(f"Error deleting avatar: {str(e)}")
        return create_error_response(message=f"Gagal hapus avatar: {str(e)}")
