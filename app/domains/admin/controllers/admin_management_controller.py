from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.core.database import get_db
from app.domains.admin.services.admin_service import AdminManagementService
from app.domains.admin.schemas.admin_schemas import (
    AdminCreate, AdminUpdate, AdminResponse, PaginatedResponse, AuditLogResponse
)
from app.shared.dependencies.admin_auth_deps import get_current_admin, get_current_super_admin
from app.domains.admin.models.admin import Admin

logger = logging.getLogger(__name__)


class AdminManagementController:
    """
    Controller untuk manajemen admin - Single Responsibility: Admin management endpoints
    """
    
    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup routes untuk manajemen admin"""
        
        @self.router.get("/", response_model=PaginatedResponse)
        async def get_admins(
            page: int = 1,
            size: int = 10,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil daftar admin"""
            admin_service = AdminManagementService(db)
            skip = (page - 1) * size
            
            admins, total = admin_service.get_admins(skip, size)
            
            return PaginatedResponse(
                items=[AdminResponse.from_orm(admin) for admin in admins],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )
        
        @self.router.post("/", response_model=AdminResponse)
        async def create_admin(
            admin_data: AdminCreate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Buat admin baru"""
            admin_service = AdminManagementService(db)
            
            admin = admin_service.create_admin(admin_data, current_admin.id)
            
            return AdminResponse.from_orm(admin)
        
        @self.router.get("/{admin_id}", response_model=AdminResponse)
        async def get_admin(
            admin_id: str,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil detail admin"""
            admin_service = AdminManagementService(db)
            
            admin = admin_service.get_admin_by_id(admin_id)
            
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin tidak ditemukan"
                )
            
            return AdminResponse.from_orm(admin)
        
        @self.router.put("/{admin_id}", response_model=AdminResponse)
        async def update_admin(
            admin_id: str,
            admin_data: AdminUpdate,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Update admin"""
            admin_service = AdminManagementService(db)
            
            admin = admin_service.update_admin(admin_id, admin_data, current_admin.id)
            
            return AdminResponse.from_orm(admin)
        
        @self.router.delete("/{admin_id}")
        async def delete_admin(
            admin_id: str,
            current_admin: Admin = Depends(get_current_super_admin),
            db: Session = Depends(get_db)
        ):
            """Hapus admin"""
            admin_service = AdminManagementService(db)
            
            success = admin_service.delete_admin(admin_id, current_admin.id)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin tidak ditemukan"
                )
            
            return {"message": "Admin berhasil dihapus"}
        
        @self.router.get("/audit-logs/", response_model=PaginatedResponse)
        async def get_audit_logs(
            page: int = 1,
            size: int = 10,
            action: Optional[str] = None,
            resource: Optional[str] = None,
            current_admin: Admin = Depends(get_current_admin),
            db: Session = Depends(get_db)
        ):
            """Ambil audit logs"""
            admin_service = AdminManagementService(db)
            skip = (page - 1) * size
            
            logs, total = admin_service.get_audit_logs(skip, size, action, resource)
            
            return PaginatedResponse(
                items=[AuditLogResponse.from_orm(log) for log in logs],
                total=total,
                page=page,
                size=size,
                pages=(total + size - 1) // size
            )


# Initialize controller
admin_management_controller = AdminManagementController()
