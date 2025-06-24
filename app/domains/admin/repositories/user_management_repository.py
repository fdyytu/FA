"""
Repository untuk manajemen user
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Dict, Tuple

from app.common.logging.admin_logger import admin_logger
from app.domains.auth.models.user import User


class UserManagementRepository:
    """
    Repository untuk manajemen user - Single Responsibility: Data access untuk user management
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("UserManagementRepository initialized")
    
    def get_users_with_pagination(
        self, 
        skip: int = 0, 
        limit: int = 10,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Ambil user dengan pagination dan filter"""
        try:
            admin_logger.info(f"Mengambil users dengan pagination - skip: {skip}, limit: {limit}")
            query = self.db.query(User)
            
            # Apply filters
            if search:
                admin_logger.info(f"Menerapkan filter search: {search}")
                query = query.filter(
                    or_(
                        User.username.ilike(f"%{search}%"),
                        User.email.ilike(f"%{search}%"),
                        User.full_name.ilike(f"%{search}%")
                    )
                )
            
            if is_active is not None:
                admin_logger.info(f"Menerapkan filter is_active: {is_active}")
                query = query.filter(User.is_active == is_active)
            
            total = query.count()
            users = query.offset(skip).limit(limit).all()
            
            admin_logger.info(f"Ditemukan {len(users)} users dari total {total}")
            return users, total
            
        except Exception as e:
            admin_logger.error("Error saat mengambil users dengan pagination", e, {
                "skip": skip, "limit": limit, "search": search, "is_active": is_active
            })
            raise
    
    def get_user_stats(self) -> Dict[str, int]:
        """Ambil statistik user"""
        try:
            admin_logger.info("Mengambil statistik user")
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            inactive_users = total_users - active_users
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users
            }
            
            admin_logger.info("Statistik user berhasil diambil", stats)
            return stats
            
        except Exception as e:
            admin_logger.error("Error saat mengambil statistik user", e)
            raise
