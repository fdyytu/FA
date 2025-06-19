#!/usr/bin/env python3
"""
Script untuk inisialisasi database
Mengatasi masalah: sqlite3.OperationalError) no such table: discord_configs
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def init_database():
    """Initialize database dengan semua tabel yang diperlukan"""
    try:
        print("🔄 Memulai inisialisasi database...")
        
        # Import database engine dan base
        from app.core.database import engine, Base
        
        # Import semua model untuk registrasi dengan SQLAlchemy
        print("📦 Mengimpor model database...")
        
        # Discord models
        from app.domains.discord.models.discord_config import DiscordConfig
        
        # Import model lainnya jika ada
        try:
            import app.domains.wallet.models.wallet
            print("✅ Wallet models imported")
        except ImportError:
            print("⚠️  Wallet models not found")
        
        try:
            import app.domains.admin.models.admin
            print("✅ Admin models imported")
        except ImportError:
            print("⚠️  Admin models not found")
        
        try:
            import app.domains.product.models.product
            print("✅ Product models imported")
        except ImportError:
            print("⚠️  Product models not found")
        
        # Buat semua tabel
        print("🏗️  Membuat tabel database...")
        Base.metadata.create_all(bind=engine)
        
        # Verifikasi tabel discord_configs
        print("🔍 Memverifikasi tabel discord_configs...")
        import sqlite3
        from app.infrastructure.config.settings import settings
        
        # Extract database path from DATABASE_URL
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            print(f"❌ Database file tidak ditemukan: {db_path}")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if discord_configs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='discord_configs';")
        result = cursor.fetchone()
        
        if result:
            print("✅ Tabel discord_configs berhasil dibuat!")
            
            # Show table structure
            cursor.execute("PRAGMA table_info(discord_configs);")
            columns = cursor.fetchall()
            print("📋 Struktur tabel discord_configs:")
            for col in columns:
                print(f"   - {col[1]} {col[2]} (nullable: {not col[3]})")
        else:
            print("❌ Tabel discord_configs tidak ditemukan!")
            conn.close()
            return False
        
        # Show all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Total tabel dalam database: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        print("🎉 Inisialisasi database berhasil!")
        return True
        
    except Exception as e:
        print(f"❌ Error saat inisialisasi database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
