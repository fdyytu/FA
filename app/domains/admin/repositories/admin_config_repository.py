"""
Repository untuk konfigurasi admin
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.common.logging.admin_logger import admin_logger
from app.domains.admin.models.admin import AdminConfig


class AdminConfigRepository:
    """
    Repository untuk konfigurasi admin - Single Responsibility: Data access untuk config
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("AdminConfigRepository initialized")
    
    def get_by_key(self, config_key: str) -> Optional[AdminConfig]:
        """Ambil konfigurasi berdasarkan key"""
        try:
            admin_logger.info(f"Mencari config dengan key: {config_key}")
            result = self.db.query(AdminConfig).filter(
                AdminConfig.config_key == config_key,
                AdminConfig.is_active == True
            ).first()
            if result:
                admin_logger.info(f"Config ditemukan: {config_key}")
            else:
                admin_logger.warning(f"Config tidak ditemukan: {config_key}")
            return result
        except Exception as e:
            admin_logger.error(f"Error saat mencari config dengan key: {config_key}", e)
            raise
    
    def get_active_configs(self) -> List[AdminConfig]:
        """Ambil semua konfigurasi aktif"""
        try:
            admin_logger.info("Mengambil semua config aktif")
            result = self.db.query(AdminConfig).filter(
                AdminConfig.is_active == True
            ).all()
            admin_logger.info(f"Ditemukan {len(result)} config aktif")
            return result
        except Exception as e:
            admin_logger.error("Error saat mengambil config aktif", e)
            raise
    
    def update_config_value(self, config_key: str, config_value: str) -> bool:
        """Update nilai konfigurasi"""
        try:
            admin_logger.info(f"Update config {config_key} dengan value: {config_value}")
            result = self.db.query(AdminConfig).filter(
                AdminConfig.config_key == config_key
            ).update({"config_value": config_value})
            self.db.commit()
            
            if result > 0:
                admin_logger.info(f"Config berhasil diupdate: {config_key}")
            else:
                admin_logger.warning(f"Config tidak ditemukan untuk update: {config_key}")
            
            return result > 0
        except Exception as e:
            admin_logger.error(f"Error saat update config {config_key}", e)
            self.db.rollback()
            raise
