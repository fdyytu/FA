from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.domains.user.services.user_management_service import UserManagementService
from app.schemas.user_profile import (
    UserDetailResponse, UserListResponse
)
from app.utils.responses import create_success_response, create_error_response
from app.middleware.security import require_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/users", response_model=dict)
async def get_users_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None, regex="^(active|inactive|all)$"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mendapatkan daftar user dengan filter dan pagination (untuk admin)"""
    try:
        service = UserManagementService(db)
        result = await service.get_users_list(page, limit, search, status)
        
        return create_success_response(
            data={
                "users": [user.dict() for user in result["users"]],
                "page": page,
                "limit": limit,
                "total": result["total"],
                "total_pages": result["total_pages"]
            },
            message="Daftar user berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting users list: {str(e)}")
        return create_error_response(message=f"Gagal mengambil daftar user: {str(e)}")

@router.get("/users/{user_id}", response_model=dict)
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mendapatkan detail user tertentu (untuk admin)"""
    try:
        service = UserManagementService(db)
        user_detail = await service.get_user_detail(user_id)
        
        return create_success_response(
            data=user_detail.dict(),
            message="Detail user berhasil diambil"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting user detail: {str(e)}")
        return create_error_response(message=f"Gagal mengambil detail user: {str(e)}")

@router.post("/users/{user_id}/toggle-status", response_model=dict)
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle status aktif/nonaktif user (untuk admin)"""
    try:
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

@router.post("/users/{user_id}/verify-identity", response_model=dict)
async def verify_user_identity(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Verifikasi identitas user (untuk admin)"""
    try:
        service = UserManagementService(db)
        profile = await service.verify_user_identity(user_id)
        
        return create_success_response(
            data=profile.dict(),
            message="Identitas user berhasil diverifikasi"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error verifying user identity: {str(e)}")
        return create_error_response(message=f"Gagal verifikasi identitas: {str(e)}")

@router.post("/users/{user_id}/reset-password", response_model=dict)
async def reset_user_password(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reset password user (untuk admin)"""
    try:
        service = UserManagementService(db)
        new_password = await service.reset_user_password(user_id)
        
        return create_success_response(
            data={"temporary_password": new_password},
            message="Password user berhasil direset. Password sementara telah digenerate."
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error resetting user password: {str(e)}")
        return create_error_response(message=f"Gagal reset password user: {str(e)}")

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Hapus user (soft delete) (untuk admin)"""
    try:
        service = UserManagementService(db)
        await service.delete_user(user_id)
        
        return create_success_response(
            data=None,
            message="User berhasil dihapus"
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return create_error_response(message=f"Gagal menghapus user: {str(e)}")

@router.get("/statistics", response_model=dict)
async def get_user_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mendapatkan statistik user untuk dashboard admin"""
    try:
        service = UserManagementService(db)
        statistics = await service.get_user_statistics()
        
        return create_success_response(
            data=statistics,
            message="Statistik user berhasil diambil"
        )
        
    except Exception as e:
        logger.error(f"Error getting user statistics: {str(e)}")
        return create_error_response(message=f"Gagal mengambil statistik user: {str(e)}")

@router.get("/export", response_model=dict)
async def export_users_data(
    format: str = Query("csv", regex="^(csv|excel)$"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Export data user ke CSV atau Excel (untuk admin)"""
    try:
        service = UserManagementService(db)
        file_url = await service.export_users_data(format)
        
        return create_success_response(
            data={"download_url": file_url},
            message=f"Data user berhasil diexport ke format {format.upper()}"
        )
        
    except Exception as e:
        logger.error(f"Error exporting users data: {str(e)}")
        return create_error_response(message=f"Gagal export data user: {str(e)}")
