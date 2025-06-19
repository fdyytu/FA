#!/usr/bin/env python3
"""
Script untuk membuat admin langsung ke database
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_admin_direct():
    """Buat admin langsung ke database"""
    try:
        from app.core.database import SessionLocal
        from app.infrastructure.security.password_handler import PasswordHandler
        from sqlalchemy import text
        
        # Buat admin
        db = SessionLocal()
        try:
            # Cek apakah sudah ada admin
            result = db.execute(text("SELECT * FROM admins LIMIT 1"))
            existing_admin = result.fetchone()
            
            if existing_admin:
                print("✅ Admin sudah ada!")
                print(f"Username: {existing_admin[1]}")  # username column
                print(f"Email: {existing_admin[2]}")     # email column
                return True
            
            # Hash password
            password_handler = PasswordHandler()
            hashed_pwd = password_handler.hash_password("admin123")
            
            # Insert admin langsung dengan SQL
            insert_sql = text("""
                INSERT INTO admins (username, email, full_name, hashed_password, is_active, role, phone_number)
                VALUES (:username, :email, :full_name, :hashed_password, :is_active, :role, :phone_number)
            """)
            
            db.execute(insert_sql, {
                'username': 'admin',
                'email': 'admin@example.com',
                'full_name': 'Super Admin',
                'hashed_password': hashed_pwd,
                'is_active': True,
                'role': 'ADMIN',
                'phone_number': None
            })
            
            db.commit()
            
            print("✅ Admin berhasil dibuat!")
            print("Username: admin")
            print("Password: admin123")
            print("Role: ADMIN")
            return True
            
        except Exception as e:
            print(f"❌ Database Error: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Membuat admin langsung ke database...")
    success = create_admin_direct()
    if success:
        print("\n🎉 Setup admin berhasil!")
        print("\n📱 Sekarang Anda bisa login:")
        print("- Username: admin")
        print("- Password: admin123")
    else:
        print("\n❌ Setup admin gagal!")
