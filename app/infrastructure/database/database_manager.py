from sqlalchemy.orm import Session
from typing import Generator
import logging

from app.infrastructure.config.settings import settings
from app.core.database import engine, SessionLocal, Base
from app.infrastructure.database.models_registry import import_all_models
from app.infrastructure.database.init_admin import ensure_admin_exists

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
            # Import semua model terlebih dahulu
            self.logger.info("Importing all database models...")
            models_imported = import_all_models()
            
            # Buat semua tabel dengan checkfirst=True untuk menghindari error jika sudah ada
            self.logger.info("Creating database tables...")
            self.Base.metadata.create_all(bind=self.engine, checkfirst=True)
            
            # Verifikasi tabel yang dibuat
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            self.logger.info(f"Database tables verified: {len(tables)} tables")
            self.logger.info(f"Models imported: {len(models_imported)} models")
            
            # Log tabel yang ada untuk debugging
            for table in tables:
                self.logger.debug(f"  - Table: {table}")
            
            # Pastikan tabel admin ada
            if 'admins' not in tables:
                self.logger.warning("Table 'admins' not found, attempting to create manually...")
                self._create_admin_table_manually()
            
            # Buat admin default jika belum ada
            self.logger.info("Checking admin existence...")
            self.ensure_default_admin()
                
        except Exception as e:
            self.logger.error(f"Error creating database tables: {str(e)}")
            # Jangan raise exception agar aplikasi tetap bisa jalan
            self.logger.info("Continuing startup despite database error...")
    
    def _create_admin_table_manually(self):
        """
        Membuat tabel admin secara manual jika tidak ada
        """
        try:
            from app.domains.admin.models.admin import Admin
            Admin.__table__.create(bind=self.engine, checkfirst=True)
            self.logger.info("Admin table created manually")
        except Exception as e:
            self.logger.error(f"Error creating admin table manually: {e}")
    
    def ensure_default_admin(self):
        """
        Memastikan ada admin default di database
        """
        try:
            db = self.get_session()
            try:
                ensure_admin_exists(db)
            finally:
                db.close()
        except Exception as e:
            self.logger.error(f"Error ensuring default admin: {str(e)}")
            # Jangan raise exception agar aplikasi tetap bisa jalan
    
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
