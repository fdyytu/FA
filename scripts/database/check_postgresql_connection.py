#!/usr/bin/env python3
"""
Script untuk mengecek koneksi ke PostgreSQL Railway
dan menampilkan informasi database
"""

import os
import sys
from pathlib import Path
import asyncio
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from urllib.parse import urlparse

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_postgresql_connection():
    """Mengecek koneksi ke PostgreSQL Railway"""
    print("🔍 Mengecek koneksi PostgreSQL Railway...")
    
    # Cek DATABASE_URL dari environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL tidak ditemukan di environment variables")
        print("💡 Pastikan Railway PostgreSQL service sudah terhubung")
        return False
    
    print(f"🔗 DATABASE_URL ditemukan: {database_url[:50]}...")
    
    # Parse URL untuk mendapatkan informasi database
    try:
        parsed = urlparse(database_url)
        print(f"📊 Database Info:")
        print(f"   - Host: {parsed.hostname}")
        print(f"   - Port: {parsed.port}")
        print(f"   - Database: {parsed.path[1:] if parsed.path else 'N/A'}")
        print(f"   - Username: {parsed.username}")
    except Exception as e:
        print(f"⚠️  Error parsing DATABASE_URL: {e}")
    
    # Test koneksi dengan SQLAlchemy
    try:
        print("\n🔄 Testing koneksi dengan SQLAlchemy...")
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Test basic query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Koneksi berhasil!")
            print(f"📋 PostgreSQL Version: {version}")
            
            # Cek tabel yang ada
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"\n📊 Tabel yang ada ({len(tables)}):")
            if tables:
                for table in tables:
                    print(f"   - {table}")
            else:
                print("   (Tidak ada tabel)")
            
            # Cek schema
            schemas = inspector.get_schema_names()
            print(f"\n🗂️  Schema yang tersedia: {schemas}")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Error koneksi SQLAlchemy: {e}")
        return False
    except Exception as e:
        print(f"❌ Error umum: {e}")
        return False

def check_environment_setup():
    """Mengecek setup environment untuk Railway"""
    print("\n🔧 Mengecek Environment Setup...")
    
    # Cek environment variables penting
    env_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'APP_NAME',
        'ENVIRONMENT'
    ]
    
    missing_vars = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'DATABASE_URL':
                print(f"✅ {var}: {value[:50]}...")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        return False
    
    return True

def test_database_operations():
    """Test operasi database dasar"""
    print("\n🧪 Testing operasi database...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL tidak tersedia")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Test create table
            print("🔄 Testing CREATE TABLE...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            connection.commit()
            print("✅ CREATE TABLE berhasil")
            
            # Test insert
            print("🔄 Testing INSERT...")
            connection.execute(text("""
                INSERT INTO test_connection (name) VALUES ('Test Connection')
            """))
            connection.commit()
            print("✅ INSERT berhasil")
            
            # Test select
            print("🔄 Testing SELECT...")
            result = connection.execute(text("SELECT * FROM test_connection"))
            rows = result.fetchall()
            print(f"✅ SELECT berhasil - {len(rows)} rows")
            
            # Cleanup
            print("🔄 Cleaning up test table...")
            connection.execute(text("DROP TABLE test_connection"))
            connection.commit()
            print("✅ Cleanup berhasil")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing database operations: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 RAILWAY POSTGRESQL CONNECTION CHECKER")
    print("=" * 60)
    
    # Check environment setup
    env_ok = check_environment_setup()
    
    # Check PostgreSQL connection
    if env_ok:
        conn_ok = check_postgresql_connection()
        
        if conn_ok:
            # Test database operations
            ops_ok = test_database_operations()
            
            if ops_ok:
                print("\n🎉 Semua test berhasil! Backend terkoneksi ke PostgreSQL Railway")
                return True
            else:
                print("\n⚠️  Koneksi berhasil tapi ada masalah dengan operasi database")
                return False
        else:
            print("\n❌ Gagal terkoneksi ke PostgreSQL Railway")
            return False
    else:
        print("\n❌ Environment setup tidak lengkap")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
