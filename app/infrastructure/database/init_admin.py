"""
Script untuk membuat admin default saat startup
"""
import logging
from sqlalchemy.orm import Session
from app.domains.admin.models.admin import Admin, AdminRole
from app.common.security.auth_security import get_password_hash

logger = logging.getLogger(__name__)

def create_default_admin(db: Session):
    """
    Membuat admin default jika belum ada admin di database
    """
    try:
        # Cek apakah sudah ada admin
        existing_admin = db.query(Admin).first()
        
        if existing_admin:
            logger.info("Admin sudah ada di database")
            return existing_admin
        
        # Buat admin default
        default_admin = Admin(
            username="admin",
            email="admin@fa.com",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            role=AdminRole.SUPER_ADMIN,
            phone_number=None
        )
        
        db.add(default_admin)
        db.commit()
        db.refresh(default_admin)
        
        logger.info(f"Admin default berhasil dibuat: {default_admin.username}")
        logger.info("Login credentials - Username: admin, Password: admin123")
        
        return default_admin
        
    except Exception as e:
        logger.error(f"Error membuat admin default: {e}")
        db.rollback()
        raise

def ensure_admin_exists(db: Session):
    """
    Memastikan minimal ada satu admin di database
    """
    try:
        admin_count = db.query(Admin).count()
        
        if admin_count == 0:
            logger.info("Tidak ada admin di database, membuat admin default...")
            return create_default_admin(db)
        else:
            logger.info(f"Database sudah memiliki {admin_count} admin")
            return None
            
    except Exception as e:
        logger.error(f"Error checking admin existence: {e}")
        raise
