"""
User Management Repository
Repository untuk data access user management operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict

from app.domains.auth.models.user import User


class UserManagementRepository:
    """
    Repository untuk manajemen user - Single Responsibility: Data access untuk user management
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_users_with_pagination(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Ambil user dengan pagination dan filter"""
        query = self.db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    def get_user_stats(self) -> Dict[str, int]:
        """Ambil statistik user"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        inactive_users = total_users - active_users
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users
        }
