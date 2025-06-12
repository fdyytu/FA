from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.user_profile_service import UserProfileService, UserManagementService
from app.schemas.user_profile import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserDetailResponse, UserListResponse
)
from app.utils.responses import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/profile", response_model=dict)
async def create_user_profile(
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

@router.get("/profile", response_model=dict)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan profil user saat ini"""
    try:
        service = UserProfileService(db)
        profile = await service.get_profile(current_user.id)
        
        if not profile:
            return create_success_response(
                data=None,
                message="Profil belum dibuat"
            )
        
        return create_success_response(
            data=profile.dict(),
            message="Profil berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return create_error_response(message=f"Gagal mengambil profil: {str(e)}")

@router.put("/profile", response_model=dict)
async def update_user_profile(
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
async def get_user_detail(
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

# Endpoints untuk admin
@router.get("/admin/users", response_model=dict)
async def get_users_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan daftar user (untuk admin)"""
    try:
        # Cek apakah user adalah admin/superuser
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = UserManagementService(db)
        users = await service.get_users_list(page, limit, search)
        
        return create_success_response(
            data={
                "users": [user.dict() for user in users],
                "page": page,
                "limit": limit,
                "total": len(users)
            },
            message="Daftar user berhasil diambil"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting users list: {str(e)}")
        return create_error_response(message=f"Gagal mengambil daftar user: {str(e)}")

@router.post("/admin/users/{user_id}/toggle-status", response_model=dict)
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle status aktif/nonaktif user (untuk admin)"""
    try:
        # Cek apakah user adalah admin/superuser
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = UserManagementService(db)
        user_detail = await service.toggle_user_status(user_id)
        
        return create_success_response(
            data=user_detail.dict(),
            message="Status user berhasil diubah"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        return create_error_response(message=f"Gagal mengubah status user: {str(e)}")

@router.post("/admin/users/{user_id}/verify-identity", response_model=dict)
async def verify_user_identity(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifikasi identitas user (untuk admin)"""
    try:
        # Cek apakah user adalah admin/superuser
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = UserProfileService(db)
        profile = await service.verify_identity(user_id)
        
        return create_success_response(
            data=profile.dict(),
            message="Identitas user berhasil diverifikasi"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error verifying user identity: {str(e)}")
        return create_error_response(message=f"Gagal verifikasi identitas: {str(e)}")

@router.get("/admin/statistics", response_model=dict)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mendapatkan statistik user untuk dashboard admin"""
    try:
        # Cek apakah user adalah admin/superuser
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Akses ditolak")
        
        service = UserManagementService(db)
        statistics = await service.get_user_statistics()
        
        return create_success_response(
            data=statistics,
            message="Statistik user berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {str(e)}")
        return create_error_response(message=f"Gagal mengambil statistik user: {str(e)}")
