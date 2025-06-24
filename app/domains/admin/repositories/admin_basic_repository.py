"""
Repository untuk operasi dasar admin
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.common.logging.admin_logger import admin_logger
from app.domains.admin.models.admin import Admin


class AdminRepository:
    """
    Repository untuk admin - Single Responsibility: Data access untuk admin
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("AdminRepository initialized")
    
    def get_by_username(self, username: str) -> Optional[Admin]:
        """Ambil admin berdasarkan username"""
        try:
            admin_logger.info(f"Mencari admin dengan username: {username}")
            result = self.db.query(Admin).filter(Admin.username == username).first()
            if result:
                admin_logger.info(f"Admin ditemukan: {username}")
            else:
                admin_logger.warning(f"Admin tidak ditemukan: {username}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari admin dengan username: {username}", e)
            raise
    
    def get_by_email(self, email: str) -> Optional[Admin]:
        """Ambil admin berdasarkan email"""
        try:
            admin_logger.info(f"Mencari admin dengan email: {email}")
            result = self.db.query(Admin).filter(Admin.email == email).first()
            if result:
                admin_logger.info(f"Admin ditemukan dengan email: {email}")
            else:
                admin_logger.warning(f"Admin tidak ditemukan dengan email: {email}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari admin dengan email: {email}", e)
            raise
    
    def create(self, admin: Admin) -> Admin:
        """Buat admin baru"""
        try:
            admin_logger.info(f"Membuat admin baru: {admin.username}")
            self.db.add(admin)
            self.db.commit()
            self.db.refresh(admin)
            admin_logger.info(f"Admin berhasil dibuat: {admin.username}")
            return admin
        except Exception as e:
            admin_logger.error(f"Error saat membuat admin: {admin.username}", e)
            self.db.rollback()
            raise
    
    def get_by_id(self, admin_id: str) -> Optional[Admin]:
        """Ambil admin berdasarkan ID"""
        try:
            admin_logger.info(f"Mencari admin dengan ID: {admin_id}")
            result = self.db.query(Admin).filter(Admin.id == admin_id).first()
            if result:
                admin_logger.info(f"Admin ditemukan dengan ID: {admin_id}")
            else:
                admin_logger.warning(f"Admin tidak ditemukan dengan ID: {admin_id}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari admin dengan ID: {admin_id}", e)
            raise
    
    def update_last_login(self, admin_id: str) -> None:
        """Update waktu login terakhir"""
        try:
            admin_logger.info(f"Update last login untuk admin ID: {admin_id}")
            self.db.query(Admin).filter(Admin.id == admin_id).update({
                "last_login": datetime.utcnow()
            })
            self.db.commit()
            admin_logger.info(f"Last login berhasil diupdate untuk admin ID: {admin_id}")
        except Exception as e:
            admin_logger.error(f"Error saat update last login untuk admin ID: {admin_id}", e)
            self.db.rollback()
            raise
