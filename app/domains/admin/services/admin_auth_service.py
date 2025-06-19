from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.models.admin import Admin
from app.domains.admin.repositories.admin_repository import AdminRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import AdminCreate
from app.common.security.auth_security import get_password_hash, verify_password


class AdminAuthService(BaseService):
    """
    Service untuk autentikasi admin - Single Responsibility: Admin authentication
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def authenticate_admin(self, username: str, password: str) -> Optional[Admin]:
        """Autentikasi admin"""
        admin = self.admin_repo.get_by_username(username)
        if not admin:
            return None
        
        if not verify_password(password, admin.hashed_password):
            return None
        
        if not admin.is_active:
            return None
        
        # Update last login
        self.admin_repo.update_last_login(admin.id)
        
        # Log login activity
        self.audit_repo.create_log(
            admin_id=admin.id,
            action="LOGIN",
            resource="admin",
            resource_id=admin.id
        )
        
        return admin
    
    def create_admin(self, admin_data: AdminCreate, creator_admin_id: str) -> Admin:
        """Buat admin baru"""
        # Check if username or email already exists
        if self.admin_repo.get_by_username(admin_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah digunakan"
            )
        
        if self.admin_repo.get_by_email(admin_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email sudah digunakan"
            )
        
        # Create admin
        admin = Admin(
            username=admin_data.username,
            email=admin_data.email,
            full_name=admin_data.full_name,
            phone_number=admin_data.phone_number,
            role=admin_data.role,
            hashed_password=get_password_hash(admin_data.password)
        )
        
        created_admin = self.admin_repo.create(admin)
        
        # Log creation
        self.audit_repo.create_log(
            admin_id=creator_admin_id,
            action="CREATE",
            resource="admin",
            resource_id=created_admin.id,
            new_values=json.dumps({
                "username": admin_data.username,
                "email": admin_data.email,
                "role": admin_data.role.value
            })
        )
        
        return created_admin
