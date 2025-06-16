from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.common.security.auth_security import verify_token
from app.domains.admin.models.admin import Admin

# Security
security = HTTPBearer()

def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Dependency untuk mendapatkan current admin dari token.
    """
    try:
        # Verifikasi token
        payload = verify_token(credentials.credentials)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
        admin_id_str = payload.get("sub")
        token_type = payload.get("type")
        
        if admin_id_str is None or token_type != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Convert admin_id to integer
        try:
            admin_id = int(admin_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin ID in token"
            )
        
        # Ambil admin dari database
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found"
            )
        
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin is inactive"
            )
        
        return admin
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

def get_current_super_admin(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """Dependency untuk mendapatkan current super admin"""
    from app.domains.admin.models.admin import AdminRole
    
    if current_admin.role != AdminRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_admin
