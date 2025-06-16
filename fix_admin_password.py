#!/usr/bin/env python3
"""
Script untuk memperbaiki password admin
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix_admin_password():
    """Perbaiki password admin"""
    try:
        from app.core.database import SessionLocal
        from app.domains.admin.models.admin import Admin
        from app.common.security.auth_security import get_password_hash, verify_password
        
        db = SessionLocal()
        try:
            # Cari admin dengan username 'admin'
            admin = db.query(Admin).filter(Admin.username == "admin").first()
            if not admin:
                print("❌ Admin dengan username 'admin' tidak ditemukan")
                return
            
            print(f"✅ Admin ditemukan: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Hash saat ini: {admin.hashed_password}")
            
            # Test beberapa password umum
            common_passwords = ["admin123", "admin", "password", "123456", "admin@123"]
            
            print("\n🔍 Mencoba password umum...")
            for pwd in common_passwords:
                if verify_password(pwd, admin.hashed_password):
                    print(f"✅ Password ditemukan: {pwd}")
                    return pwd
            
            print("❌ Password umum tidak cocok")
            
            # Set password baru
            new_password = "admin123"
            new_hash = get_password_hash(new_password)
            
            admin.hashed_password = new_hash
            db.commit()
            
            print(f"✅ Password berhasil direset!")
            print(f"Username: admin")
            print(f"Password baru: {new_password}")
            
            return new_password
            
        except Exception as e:
            print(f"❌ Database Error: {e}")
            db.rollback()
            return None
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🔧 Memperbaiki password admin...")
    password = fix_admin_password()
    if password:
        print("\n🎉 Password admin berhasil diperbaiki!")
        print("\n📱 Sekarang Anda bisa login dengan:")
        print("- Username: admin")
        print(f"- Password: {password}")
