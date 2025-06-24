from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.user_management_service import UserManagementService
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class UserValidationController:
    """
    Controller untuk validasi dan manajemen status user - Single Responsibility: User validation operations
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk validasi user"""
        
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
user_validation_controller = UserValidationController()
