from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict
import json

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import UserManagementRepository, AuditLogRepository
from app.domains.admin.schemas.admin_schemas import UserUpdateByAdmin
from app.domains.auth.models.user import User

class UserManagementService(BaseService):
    """Service untuk manajemen user - Single Responsibility: User management by admin"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserManagementRepository(db)
        self.audit_repo = AuditLogRepository(db)
    
    def get_users(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Ambil daftar user dengan filter"""
        return self.user_repo.get_users_with_pagination(skip, limit, search, is_active)
    
    def get_user_stats(self) -> Dict[str, int]:
        """Ambil statistik user"""
        return self.user_repo.get_user_stats()
    
    def update_user(
        self,
        user_id: str,
        user_data: UserUpdateByAdmin,
        admin_id: str
    ) -> User:
        """Update user oleh admin"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User tidak ditemukan"
            )
        
        # Store old values
        old_values = {
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "is_active": user.is_active,
            "balance": str(user.balance)
        }
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        # Log update
        self.audit_repo.create_log(
            admin_id=admin_id,
            action="UPDATE",
            resource="user",
            resource_id=user_id,
            old_values=json.dumps(old_values),
            new_values=json.dumps(update_data, default=str)
        )
        
        return user
