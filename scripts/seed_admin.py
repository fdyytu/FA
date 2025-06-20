#!/usr/bin/env python3
"""
Script untuk membuat admin default
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.admin.models.admin import Admin, AdminRole
from app.domains.admin.repositories.admin_repository import AdminRepository
from app.common.security.auth_security import get_password_hash

def create_default_admin():
    """Buat admin default jika belum ada"""
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

if __name__ == "__main__":
    try:
        create_default_admin()
        print("Seeding admin selesai")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
