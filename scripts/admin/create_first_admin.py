#!/usr/bin/env python3
"""
Script untuk membuat admin pertama
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_first_admin():
    """Buat admin pertama untuk login dashboard"""
    try:
        from app.core.database import SessionLocal
        from app.domains.admin.models.admin import Admin, AdminRole
        from app.infrastructure.security.password_handler import PasswordHandler
        
        db = SessionLocal()
        
        try:
            # Cek apakah sudah ada admin
            existing_admin = db.query(Admin).first()
            if existing_admin:
                print("✅ Admin sudah ada!")
                print(f"Username: {existing_admin.username}")
                print(f"Email: {existing_admin.email}")
                return existing_admin
            
            # Buat admin pertama
            password_handler = PasswordHandler()
            hashed_pwd = password_handler.hash_password("admin123")
            admin = Admin(
                username="admin",
                email="admin@example.com", 
                full_name="Super Admin",
                hashed_password=hashed_pwd,
                role=AdminRole.SUPER_ADMIN,
                is_active=True
            )
            
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            print("✅ Admin pertama berhasil dibuat!")
            print("Username: admin")
            print("Password: admin123")
            print("Role: SUPER_ADMIN")
            return admin
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
            return None
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Pastikan semua dependencies sudah terinstall")
        return None

if __name__ == "__main__":
    print("🔧 Membuat admin pertama...")
    admin = create_first_admin()
    if admin:
        print("\n🎉 Setup admin berhasil!")
        print("\n📱 Akses dashboard:")
        print("- API Docs: /docs")
        print("- Admin Login: /api/v1/admin/auth/login")
        print("- Admin Dashboard: /api/v1/admin/dashboard/")
