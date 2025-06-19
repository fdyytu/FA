from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.admin_service import AdminAuthService
from app.domains.admin.schemas.admin_schemas import (
    AdminLogin, AdminLoginResponse, AdminResponse
)
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.security.auth_security import create_access_token
from app.common.responses.api_response import APIResponse

logger = logging.getLogger(__name__)


class AdminAuthController:
    """
    Controller untuk autentikasi admin - Single Responsibility: Admin authentication endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk autentikasi admin"""
        
        @self.router.post("/login", response_model=AdminLoginResponse)
        async def login_admin(
            login_data: AdminLogin,
            request: Request,
            db: Session = Depends(get_db)
        ):
            """Login admin"""
            auth_service = AdminAuthService(db)
            
            admin = auth_service.authenticate_admin(
                login_data.username, 
                login_data.password
            )
            
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Username atau password salah"
                )
            
            # Create access token
            access_token = create_access_token(
                data={"sub": str(admin.id), "type": "admin"}
            )
            
            return AdminLoginResponse(
                access_token=access_token,
                admin=AdminResponse.from_orm(admin)
            )
        
        @self.router.post("/logout")
        async def logout_admin(
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Logout admin"""
            # Log logout activity
            from app.domains.admin.repositories.admin_repository import AuditLogRepository
            audit_repo = AuditLogRepository(db)
            audit_repo.create_log(
                admin_id=current_admin.id,
                action="LOGOUT",
                resource="admin",
                resource_id=current_admin.id
            )
            
            return APIResponse.success(message="Logout berhasil")


# Initialize controller
auth_controller = AdminAuthController()
