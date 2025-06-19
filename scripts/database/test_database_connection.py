#!/usr/bin/env python3
"""
Script untuk menguji koneksi database PostgreSQL Railway
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test koneksi ke database PostgreSQL Railway"""
    try:
        # Import settings
        from app.infrastructure.config.settings import settings
        
        print("=== Test Koneksi Database PostgreSQL Railway ===")
        print(f"Database URL: {settings.DATABASE_URL[:50]}...")
        print(f"Database Type: {'PostgreSQL' if settings.is_postgresql else 'SQLite'}")
        
        # Test dengan database_manager yang sudah diperbaiki
        from app.infrastructure.database.database_manager import db_manager
        
        print("\nTesting database connection...")
        
        # Test koneksi dengan membuat session
        session = db_manager.get_session()
        
        # Test query sederhana
        from sqlalchemy import text
        result = session.execute(text("SELECT 1 as test"))
        test_result = result.fetchone()
        
        if test_result and test_result[0] == 1:
            print("✅ Koneksi database berhasil!")
            print(f"✅ Query test berhasil: {test_result[0]}")
        else:
            print("❌ Query test gagal")
            
        session.close()
        
        # Test dengan core.database
        print("\nTesting core database engine...")
        from app.core.database import engine
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"✅ PostgreSQL Version: {version[0]}")
            
        print("\n🎉 Semua test koneksi database berhasil!")
        return True
        
    except Exception as e:
        print(f"❌ Error koneksi database: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
