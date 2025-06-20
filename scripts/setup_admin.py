#!/usr/bin/env python3
"""
Script untuk membuat tabel admin dan seeding data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.database_manager import db_manager
from app.domains.admin.models.admin import Admin, AdminRole, AdminConfig, PPOBMarginConfig, AdminAuditLog, AdminNotificationSetting
from app.domains.admin.repositories.admin_repository import AdminRepository
from app.common.security.auth_security import get_password_hash
from app.core.database import get_db

def create_admin_tables():
    """Buat tabel admin"""
    try:
        # Import semua model admin
        from app.domains.admin.models.admin import Admin, AdminConfig, PPOBMarginConfig, AdminAuditLog, AdminNotificationSetting
        
        # Buat tabel
        db_manager.create_tables()
        print("Tabel admin berhasil dibuat")
        return True
    except Exception as e:
        print(f"Error membuat tabel: {e}")
        return False

def create_default_admin():
    """Buat admin default"""
    try:
        db = next(get_db())
        admin_repo = AdminRepository(db)
        
        # Check if admin already exists
        existing_admin = admin_repo.get_by_username("admin")
        if existing_admin:
            print("Admin default sudah ada")
            return existing_admin
        
        # Create default admin
        admin = Admin(
            username="admin",
            email="admin@fa-app.com",
            full_name="Administrator",
            phone_number="+62812345678",
            role=AdminRole.SUPER_ADMIN,
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        created_admin = admin_repo.create(admin)
        print(f"Admin default berhasil dibuat: {created_admin.username}")
        return created_admin
    except Exception as e:
        print(f"Error membuat admin: {e}")
        return None

def create_default_configs():
    """Buat konfigurasi default"""
    try:
        db = next(get_db())
        
        default_configs = [
            {
                "config_key": "app_name",
                "config_value": "FA Application",
                "config_type": "string",
                "description": "Nama aplikasi"
            },
            {
                "config_key": "app_version",
                "config_value": "2.0",
                "config_type": "string",
                "description": "Versi aplikasi"
            },
            {
                "config_key": "maintenance_mode",
                "config_value": "false",
                "config_type": "boolean",
                "description": "Mode maintenance"
            }
        ]
        
        for config_data in default_configs:
            existing = db.query(AdminConfig).filter(
                AdminConfig.config_key == config_data["config_key"]
            ).first()
            
            if not existing:
                config = AdminConfig(**config_data)
                db.add(config)
        
        db.commit()
        print("Konfigurasi default berhasil dibuat")
        return True
    except Exception as e:
        print(f"Error membuat konfigurasi: {e}")
        return False

if __name__ == "__main__":
    print("Memulai setup admin...")
    
    # 1. Buat tabel
    if not create_admin_tables():
        sys.exit(1)
    
    # 2. Buat admin default
    if not create_default_admin():
        sys.exit(1)
    
    # 3. Buat konfigurasi default
    if not create_default_configs():
        sys.exit(1)
    
    print("Setup admin selesai!")
