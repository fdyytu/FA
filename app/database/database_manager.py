from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.infrastructure.config.settings import settings

class DatabaseManager:
    """
    Database manager yang mengimplementasikan Single Responsibility Principle.
    Fokus hanya pada manajemen koneksi database.
    """
    
    def __init__(self):
        self.database_url = settings.DATABASE_URL
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.Base = declarative_base()
    
    def get_db(self):
        """Dependency untuk mendapatkan database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def create_tables(self):
        """Buat semua tabel database"""
        self.Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Hapus semua tabel database"""
        self.Base.metadata.drop_all(bind=self.engine)

# Global database manager instance
db_manager = DatabaseManager()

# Exports untuk backward compatibility
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal
Base = db_manager.Base
get_db = db_manager.get_db
