"""
Modul ini berisi implementasi logout controller untuk admin.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.common.dependencies.admin_auth_deps import get_current_admin
from app.domains.admin.models.admin import Admin
from app.common.responses.api_response import APIResponse
from app.domains.admin.repositories.admin_repository import AuditLogRepository

router = APIRouter()

@router.post("/logout")
async def logout_admin(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Logout admin"""
    # Log logout activity
    audit_repo = AuditLogRepository(db)
    audit_repo.create_log(
        admin_id=current_admin.id,
        action="LOGOUT",
        resource="admin",
        resource_id=current_admin.id
    )
    
    return APIResponse.success(message="Logout berhasil")

__all__ = ['router']
