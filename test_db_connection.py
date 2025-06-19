#!/usr/bin/env python3
"""
Script untuk test koneksi database PostgreSQL Railway
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
        
        print(f"Testing database connection...")
        print(f"Database URL: {settings.DATABASE_URL[:50]}...")
        print(f"Is PostgreSQL: {settings.is_postgresql}")
        print(f"Is SQLite: {settings.is_sqlite}")
        
        # Test SQLAlchemy connection
        from sqlalchemy import create_engine, text
        
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful! Test query result: {row[0]}")
            
            # Test database info
            if settings.is_postgresql:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()
                print(f"✅ PostgreSQL version: {version[0]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
