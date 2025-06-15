"""
Discord Configuration Repository
Repository untuk mengelola data konfigurasi Discord di database
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.domains.discord.models.discord_config import DiscordConfig


class DiscordConfigRepository:
    """Repository untuk mengelola konfigurasi Discord"""
    
    def __init__(self):
        self.model = DiscordConfig
    
    def get_active_config(self, db: Session) -> Optional[DiscordConfig]:
        """Ambil konfigurasi yang aktif"""
        return db.query(self.model).filter(
            and_(
                self.model.is_active == True,
                self.model.token.isnot(None)
            )
        ).first()
    
    def get_by_name(self, db: Session, name: str) -> Optional[DiscordConfig]:
        """Ambil konfigurasi berdasarkan nama"""
        return db.query(self.model).filter(self.model.name == name).first()
    
    def get_all_active(self, db: Session) -> List[DiscordConfig]:
        """Ambil semua konfigurasi yang aktif"""
        return db.query(self.model).filter(self.model.is_active == True).all()
    
    def deactivate_all(self, db: Session, exclude_id: Optional[int] = None) -> int:
        """Deactivate semua konfigurasi kecuali yang dikecualikan"""
        query = db.query(self.model).filter(self.model.is_active == True)
        
        if exclude_id:
            query = query.filter(self.model.id != exclude_id)
        
        count = query.count()
        query.update({"is_active": False})
        db.commit()
        
        return count
    
    def get_configs_by_guild(self, db: Session, guild_id: str) -> List[DiscordConfig]:
        """Ambil konfigurasi berdasarkan guild ID"""
        return db.query(self.model).filter(self.model.guild_id == guild_id).all()
    
    def count_active_configs(self, db: Session) -> int:
        """Hitung jumlah konfigurasi aktif"""
        return db.query(self.model).filter(self.model.is_active == True).count()
    
    def get_by_id(self, db: Session, config_id: int) -> Optional[DiscordConfig]:
        """Ambil konfigurasi berdasarkan ID"""
        return db.query(self.model).filter(self.model.id == config_id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[DiscordConfig]:
        """Ambil semua konfigurasi"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, config_data: Dict[str, Any]) -> DiscordConfig:
        """Buat konfigurasi baru"""
        db_config = self.model(**config_data)
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        return db_config
    
    def update(self, db: Session, config_id: int, update_data: Dict[str, Any]) -> Optional[DiscordConfig]:
        """Update konfigurasi"""
        db_config = self.get_by_id(db, config_id)
        if db_config:
            for field, value in update_data.items():
                setattr(db_config, field, value)
            db.commit()
            db.refresh(db_config)
        return db_config
    
    def delete(self, db: Session, config_id: int) -> bool:
        """Hapus konfigurasi"""
        db_config = self.get_by_id(db, config_id)
        if db_config:
            db.delete(db_config)
            db.commit()
            return True
        return False


# Global repository instance
discord_config_repository = DiscordConfigRepository()
