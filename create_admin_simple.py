#!/usr/bin/env python3
"""
Script sederhana untuk membuat admin pertama
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_admin_simple():
    """Buat admin dengan cara sederhana"""
    try:
        # Import yang diperlukan
        from app.core.database import SessionLocal, engine, Base
        from app.infrastructure.security.password_handler import PasswordHandler
        from sqlalchemy import Column, String, Text, Boolean, Enum
        import enum
        
        # Buat tabel admin secara manual
        class AdminRole(enum.Enum):
            SUPER_ADMIN = "super_admin"
            ADMIN = "admin"
            OPERATOR = "operator"
        
        class Admin(Base):
            __tablename__ = "admins"
            
            id = Column(String, primary_key=True, default=lambda: str(__import__('uuid').uuid4()))
            username = Column(String(50), unique=True, index=True, nullable=False)
            email = Column(String(100), unique=True, index=True, nullable=False)
            full_name = Column(String(100), nullable=False)
            hashed_password = Column(Text, nullable=False)
            is_active = Column(Boolean, default=True)
            role = Column(Enum(AdminRole), default=AdminRole.ADMIN)
            phone_number = Column(String(20), nullable=True)
            created_at = Column(String, default=lambda: __import__('datetime').datetime.utcnow().isoformat())
            updated_at = Column(String, default=lambda: __import__('datetime').datetime.utcnow().isoformat())
        
        # Buat tabel
        Base.metadata.create_all(bind=engine)
        
        # Buat admin
        db = SessionLocal()
        try:
            # Cek apakah sudah ada admin
            existing_admin = db.query(Admin).first()
            if existing_admin:
                print("✅ Admin sudah ada!")
                print(f"Username: {existing_admin.username}")
                print(f"Email: {existing_admin.email}")
                return existing_admin
            
            # Hash password
            password_handler = PasswordHandler()
            hashed_pwd = password_handler.hash_password("admin123")
            
            # Buat admin baru
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
            
            print("✅ Admin berhasil dibuat!")
            print("Username: admin")
            print("Password: admin123")
            print("Role: SUPER_ADMIN")
            return admin
            
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
    print("🔧 Membuat admin dengan cara sederhana...")
    admin = create_admin_simple()
    if admin:
        print("\n🎉 Setup admin berhasil!")
        print("\n📱 Sekarang Anda bisa login:")
        print("- Username: admin")
        print("- Password: admin123")
