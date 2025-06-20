"""
Admin Config Repository
Repository untuk data access admin configuration
"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.domains.admin.models.admin import AdminConfig


class AdminConfigRepository:
    """
    Repository untuk konfigurasi admin - Single Responsibility: Data access untuk config
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_key(self, config_key: str) -> Optional[AdminConfig]:
        """Ambil konfigurasi berdasarkan key"""
        return self.db.query(AdminConfig).filter(
            AdminConfig.config_key == config_key,
            AdminConfig.is_active == True
        ).first()
    
    def get_active_configs(self) -> List[AdminConfig]:
        """Ambil semua konfigurasi aktif"""
        return self.db.query(AdminConfig).filter(
            AdminConfig.is_active == True
        ).all()
    
    def update_config_value(self, config_key: str, config_value: str) -> bool:
        """Update nilai konfigurasi"""
        result = self.db.query(AdminConfig).filter(
            AdminConfig.config_key == config_key
        ).update({"config_value": config_value})
        self.db.commit()
        return result > 0
