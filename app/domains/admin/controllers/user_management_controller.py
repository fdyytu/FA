from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.domains.admin.services.admin_service import UserManagementService
from app.domains.admin.schemas.admin_schemas import (
    UserManagementResponse, UserUpdateByAdmin, PaginatedResponse
)
from app.shared.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.shared.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class UserManagementController:
    """
    Controller untuk manajemen user - Single Responsibility: User management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen user"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_users(
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None,
            is_active: Optional[bool] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar user"""
            user_service = UserManagementService(db)
            skip = (page - 1) * size
            
            users, total = user_service.get_users(skip, size, search, is_active)
            
            return PaginatedResponse(
                items=[UserManagementResponse.from_orm(user) for user in users],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.get("/stats")
        async def get_user_stats(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil statistik user"""
            user_service = UserManagementService(db)
            
            stats = user_service.get_user_stats()
            
            return APIResponse.success(data=stats)
        
        @self.router.get("/{user_id}", response_model=UserManagementResponse)
        async def get_user(
            user_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil detail user"""
            user_service = UserManagementService(db)
            
            user = user_service.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            return UserManagementResponse.from_orm(user)
        
        @self.router.put("/{user_id}", response_model=UserManagementResponse)
        async def update_user(
            user_id: str,
            user_data: UserUpdateByAdmin,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Update user"""
            user_service = UserManagementService(db)
            
            user = user_service.update_user(user_id, user_data, current_admin.id)
            
            return UserManagementResponse.from_orm(user)
        
        @self.router.delete("/{user_id}")
        async def delete_user(
            user_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus user"""
            user_service = UserManagementService(db)
            
            success = user_service.delete_user(user_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            return APIResponse.success(message="User berhasil dihapus")
        
        @self.router.post("/{user_id}/activate")
        async def activate_user(
            user_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Aktifkan user"""
            user_service = UserManagementService(db)
            
            success = user_service.activate_user(user_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            return APIResponse.success(message="User berhasil diaktifkan")
        
        @self.router.post("/{user_id}/deactivate")
        async def deactivate_user(
            user_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Nonaktifkan user"""
            user_service = UserManagementService(db)
            
            success = user_service.deactivate_user(user_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            return APIResponse.success(message="User berhasil dinonaktifkan")
        
        @self.router.post("/{user_id}/reset-password")
        async def reset_user_password(
            user_id: str,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Reset password user"""
            user_service = UserManagementService(db)
            
            new_password = user_service.reset_user_password(user_id, current_admin.id)
            
            if not new_password:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User tidak ditemukan"
                )
            
            return APIResponse.success(
                data={"new_password": new_password},
                message="Password user berhasil direset"
            )


# Initialize controller
user_management_controller = UserManagementController()
