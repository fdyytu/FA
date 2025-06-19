#!/usr/bin/env python3
"""
Script untuk membuat admin dengan custom ID dan password
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_custom_admin():
    """Buat admin dengan custom credentials"""
    try:
        from app.core.database import SessionLocal
        from app.domains.admin.models.admin import Admin, AdminRole
        from app.infrastructure.security.password_handler import PasswordHandler
        
        # Input custom credentials
        print("🔧 Setup Admin Custom")
        print("=" * 40)
        
        username = input("Masukkan username admin: ").strip()
        if not username:
            username = "admin"
            
        email = input("Masukkan email admin: ").strip()
        if not email:
            email = "admin@example.com"
            
        password = input("Masukkan password admin: ").strip()
        if not password:
            password = "admin123"
            
        full_name = input("Masukkan nama lengkap admin: ").strip()
        if not full_name:
            full_name = "Super Admin"
            
        phone = input("Masukkan nomor telepon (optional): ").strip()
        if not phone:
            phone = None
        
        db = SessionLocal()
        
        try:
            # Cek apakah username sudah ada
            existing_admin = db.query(Admin).filter(Admin.username == username).first()
            if existing_admin:
                print(f"❌ Username '{username}' sudah ada!")
                return None
            
            # Cek apakah email sudah ada
            existing_email = db.query(Admin).filter(Admin.email == email).first()
            if existing_email:
                print(f"❌ Email '{email}' sudah ada!")
                return None
            
            # Buat admin baru
            password_handler = PasswordHandler()
            hashed_pwd = password_handler.hash_password(password)
            
            admin = Admin(
                username=username,
                email=email, 
                full_name=full_name,
                hashed_password=hashed_pwd,
                role=AdminRole.SUPER_ADMIN,
                is_active=True,
                phone_number=phone
            )
            
            db.add(admin)
            db.commit()
            db.refresh(admin)
            
            print("\n✅ Admin berhasil dibuat!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"Role: SUPER_ADMIN")
            print(f"Phone: {phone or 'Tidak ada'}")
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

def list_existing_admins():
    """Tampilkan daftar admin yang sudah ada"""
    try:
        from app.core.database import SessionLocal
        from app.domains.admin.models.admin import Admin
        
        db = SessionLocal()
        
        try:
            admins = db.query(Admin).all()
            
            if not admins:
                print("\n📋 Belum ada admin yang terdaftar")
                return
            
            print("\n📋 Daftar Admin yang sudah ada:")
            print("=" * 50)
            for i, admin in enumerate(admins, 1):
                print(f"{i}. Username: {admin.username}")
                print(f"   Email: {admin.email}")
                print(f"   Nama: {admin.full_name}")
                print(f"   Role: {admin.role}")
                print(f"   Status: {'Aktif' if admin.is_active else 'Tidak Aktif'}")
                print(f"   Phone: {admin.phone_number or 'Tidak ada'}")
                print("-" * 30)
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")

if __name__ == "__main__":
    print("🔧 Custom Admin Creator")
    print("=" * 40)
    
    while True:
        print("\nPilih opsi:")
        print("1. Buat admin baru")
        print("2. Lihat daftar admin")
        print("3. Keluar")
        
        choice = input("\nMasukkan pilihan (1-3): ").strip()
        
        if choice == "1":
            admin = create_custom_admin()
            if admin:
                print("\n🎉 Setup admin berhasil!")
                print("\n📱 Akses dashboard:")
                print("- API Docs: /docs")
                print("- Admin Login: /api/v1/admin/auth/login")
                print("- Admin Dashboard: /api/v1/admin/dashboard/")
        elif choice == "2":
            list_existing_admins()
        elif choice == "3":
            print("\n👋 Terima kasih!")
            break
        else:
            print("\n❌ Pilihan tidak valid!")
