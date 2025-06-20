"""
Admin Repository
Repository untuk data access admin basic operations
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.common.base_classes.base_repository import BaseRepository
from app.domains.admin.models.admin import Admin


class AdminRepository:
    """
    Repository untuk admin - Single Responsibility: Data access untuk admin
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_username(self, username: str) -> Optional[Admin]:
        """Ambil admin berdasarkan username"""
        return self.db.query(Admin).filter(Admin.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[Admin]:
        """Ambil admin berdasarkan email"""
        return self.db.query(Admin).filter(Admin.email == email).first()
    
    def update_last_login(self, admin_id: str) -> None:
        """Update waktu login terakhir"""
        self.db.query(Admin).filter(Admin.id == admin_id).update({
            "last_login": datetime.utcnow()
        })
        self.db.commit()
