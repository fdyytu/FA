from sqlalchemy.orm import Session
from typing import Generator
import logging

from app.infrastructure.config.settings import settings
from app.core.database import engine, SessionLocal, Base

class DatabaseManager:
    """
    Database manager class untuk mengelola koneksi dan operasi database
    """
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        self.Base = Base
        self.logger = logging.getLogger(__name__)
    
    def create_tables(self):
        """
        Membuat semua tabel yang didefinisikan dalam model
        """
        try:
            self.Base.metadata.create_all(bind=self.engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating database tables: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """
        Mendapatkan session database
        """
        return self.SessionLocal()
    
    def get_db(self) -> Generator[Session, None, None]:
        """Dependency to get database session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Instance global dari DatabaseManager
db_manager = DatabaseManager()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session - untuk kompatibilitas"""
    return db_manager.get_db()
