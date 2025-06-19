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

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login", response_model=AdminLoginResponse)
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

__all__ = ['router']
