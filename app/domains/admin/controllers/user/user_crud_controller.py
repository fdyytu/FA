from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.domains.admin.services.user_management_service import UserManagementService
from app.domains.admin.schemas.admin_schemas import (
    UserManagementResponse, UserUpdateByAdmin, PaginatedResponse
)
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class UserCrudController:
    """
    Controller untuk operasi CRUD user - Single Responsibility: User CRUD operations
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk CRUD user"""
        
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


# Initialize controller
user_crud_controller = UserCrudController()
