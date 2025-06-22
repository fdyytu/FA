#!/usr/bin/env python3
"""
Script untuk menambahkan konfigurasi Discord Bot dengan token dan admin ID dari environment variables
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_discord_bot():
    """Setup Discord bot dengan token dan admin ID dari environment variables"""
    try:
        from app.core.database import SessionLocal
        from app.domains.discord.services.discord_config_service import discord_config_service
        from app.domains.discord.schemas.discord_config_schemas import DiscordConfigCreate
        from app.domains.admin.models.admin import Admin, AdminRole, AdminConfig
        from app.infrastructure.security.password_handler import PasswordHandler
        
        db = SessionLocal()
        
        try:
            print("🔧 Setting up Discord Bot...")
            
            # 1. Ambil konfigurasi dari environment variables
            discord_token = os.getenv("DISCORD_TOKEN")
            admin_id = os.getenv("DISCORD_ADMIN_ID", "1035189920488235120")
            
            if not discord_token:
                print("❌ DISCORD_TOKEN tidak ditemukan di environment variables")
                print("Pastikan file .env sudah dikonfigurasi dengan benar")
                print("Contoh: DISCORD_TOKEN=your_discord_bot_token_here")
                return False
            
            # Cek apakah sudah ada konfigurasi Discord aktif
            existing_config = discord_config_service.get_active_config(db)
            if existing_config:
                print("✅ Konfigurasi Discord sudah ada!")
                print(f"Config Name: {existing_config.name}")
                print(f"Command Prefix: {existing_config.command_prefix}")
            else:
                # Buat konfigurasi Discord baru
                discord_config_data = DiscordConfigCreate(
                    name="Main Discord Bot",
                    token=discord_token,
                    guild_id="",  # Akan diisi otomatis saat bot join guild
                    command_prefix="!",
                    is_active=True
                )
                
                new_config = discord_config_service.create_config(db, discord_config_data)
                print("✅ Konfigurasi Discord berhasil dibuat!")
                print(f"Config ID: {new_config.id}")
                print(f"Config Name: {new_config.name}")
            
            # 2. Buat admin jika belum ada
            existing_admin = db.query(Admin).first()
            if existing_admin:
                print("✅ Admin sudah ada!")
                print(f"Username: {existing_admin.username}")
                print(f"Email: {existing_admin.email}")
            else:
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
            
            # 3. Simpan Discord Admin ID ke konfigurasi
            discord_admin_config = db.query(AdminConfig).filter(
                AdminConfig.config_key == "discord_admin_id"
            ).first()
            
            if discord_admin_config:
                discord_admin_config.config_value = admin_id
                print("✅ Discord Admin ID berhasil diupdate!")
            else:
                discord_admin_config = AdminConfig(
                    config_key="discord_admin_id",
                    config_value=admin_id,
                    config_type="string",
                    description="Discord Admin User ID untuk bot management",
                    is_active=True
                )
                db.add(discord_admin_config)
                print("✅ Discord Admin ID berhasil ditambahkan!")
            
            db.commit()
            
            print("\n🎉 Setup Discord Bot berhasil!")
            print("\n📋 Informasi Bot:")
            print(f"- Discord Token: Configured from environment")
            print(f"- Discord Admin ID: {admin_id}")
            print(f"- Command Prefix: !")
            print("\n📱 Akses Dashboard:")
            print("- API Docs: /docs")
            print("- Admin Login: /api/v1/admin/auth/login")
            print("- Discord Dashboard: /api/v1/admin/discord/")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Pastikan semua dependencies sudah terinstall")
        return False

if __name__ == "__main__":
    print("🚀 Menambahkan Discord Bot...")
    success = setup_discord_bot()
    if success:
        print("\n✅ Setup selesai! Bot Discord siap digunakan.")
        print("\n📝 Langkah selanjutnya:")
        print("1. Pastikan bot sudah diundang ke Discord server")
        print("2. Jalankan aplikasi: python main.py")
        print("3. Test bot melalui API: /api/v1/discord/bot/status")
    else:
        print("\n❌ Setup gagal! Periksa error di atas.")
