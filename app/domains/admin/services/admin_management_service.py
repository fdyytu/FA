from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.models.admin import Admin
from app.domains.admin.repositories.admin_repository import AdminRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import AdminUpdate

class AdminManagementService(BaseService):
    """Service untuk manajemen admin - Single Responsibility: Admin management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_admins(self, skip: int = 0, limit: int = 10) -> tuple[List[Admin], int]:
        """Ambil daftar admin dengan pagination"""
        return self.admin_repo.get_all_with_pagination(skip, limit)
    
    def get_admin_by_id(self, admin_id: str) -> Admin:
        """Ambil admin berdasarkan ID"""
        admin = self.admin_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin tidak ditemukan"
            )
        return admin
    
    def update_admin(
        self, 
        admin_id: str, 
        admin_data: AdminUpdate, 
        updater_admin_id: str
    ) -> Admin:
        """Update admin"""
        admin = self.get_admin_by_id(admin_id)
        
        # Store old values for audit
        old_values = {
            "full_name": admin.full_name,
            "email": admin.email,
            "phone_number": admin.phone_number,
            "role": admin.role.value if admin.role else None,
            "is_active": admin.is_active
        }
        
        # Update fields
        update_data = admin_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(admin, field, value)
        
        updated_admin = self.admin_repo.update(admin)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=updater_admin_id,
            action="UPDATE",
            resource="admin",
            resource_id=admin_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data)
        )
        
        return updated_admin
    
    def delete_admin(self, admin_id: str, deleter_admin_id: str) -> bool:
        """Hapus admin (soft delete)"""
        admin = self.get_admin_by_id(admin_id)
        
        # Prevent self-deletion
        if admin_id == deleter_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tidak dapat menghapus akun sendiri"
            )
        
        result = self.admin_repo.delete(admin_id)
        
        if result:
            # Log deletion
            self.audit_repo.create_log(
                admin_id=deleter_admin_id,
                action="DELETE",
                resource="admin",
                resource_id=admin_id
            )
        
        return result
