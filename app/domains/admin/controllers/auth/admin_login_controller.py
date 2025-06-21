"""
Modul ini berisi implementasi login controller untuk admin.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.domains.admin.services.admin_auth_service import AdminAuthService
from app.domains.admin.schemas.admin_schemas import (
    AdminLogin, AdminLoginResponse, AdminResponse
)
from app.common.security.auth_security import create_access_token
from app.common.logging.endpoint_logger import endpoint_logger, log_endpoint_error

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=AdminLoginResponse)
@endpoint_logger("/api/v1/admin/auth/login")
async def login_admin(
    login_data: AdminLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login admin dengan enhanced logging"""
    try:
        auth_service = AdminAuthService(db)
        
        # Log login attempt
        logger.info(f"🔐 Admin login attempt for username: {login_data.username}")
        
        admin = auth_service.authenticate_admin(
            login_data.username, 
            login_data.password
        )
        
        if not admin:
            logger.warning(f"🚫 Failed login attempt for username: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username atau password salah"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(admin.id), "type": "admin"}
        )
        
        logger.info(f"✅ Successful admin login for: {admin.username}")
        
        return AdminLoginResponse(
            access_token=access_token,
            admin=AdminResponse.from_orm(admin)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        log_endpoint_error("/api/v1/admin/auth/login", e, request)
        logger.error(f"💥 Unexpected error in admin login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan sistem saat login"
        )

__all__ = ['router']
