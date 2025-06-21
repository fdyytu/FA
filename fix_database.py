#!/usr/bin/env python3
"""
Script untuk memperbaiki database dan membuat tabel admins
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix_database():
    """Perbaiki database dengan membuat tabel yang diperlukan"""
    try:
        print("🔧 Memperbaiki database...")
        
        # Import dependencies
        from app.core.database import engine, Base
        from app.domains.admin.models.admin import Admin, AdminConfig, AdminAuditLog, AdminNotificationSetting
        from app.domains.discord.models.discord_config import DiscordConfig
        
        # Hapus database lama jika ada
        db_file = "fa_database.db"
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"🗑️  Database lama dihapus: {db_file}")
        
        # Buat tabel baru
        print("🏗️  Membuat tabel baru...")
        Base.metadata.create_all(bind=engine)
        
        # Verifikasi tabel admins
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admins';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Tabel admins berhasil dibuat!")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(admins);")
            columns = cursor.fetchall()
            print("📋 Struktur tabel admins:")
            for col in columns:
                print(f"   - {col[1]} {col[2]}")
        else:
            print("❌ Tabel admins tidak ditemukan!")
            return False
        
        # Show all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Total tabel dalam database: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        print("🎉 Database berhasil diperbaiki!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database()
    sys.exit(0 if success else 1)
