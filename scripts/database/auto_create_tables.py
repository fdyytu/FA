#!/usr/bin/env python3
"""
Script untuk auto-create tabel database
Mendukung PostgreSQL Railway dan SQLite
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def import_all_models():
    """Import semua model untuk registrasi dengan SQLAlchemy Base"""
    print("📦 Mengimpor semua model database...")
    
    models_imported = []
    
    try:
        # Discord models
        from app.domains.discord.models.discord_config import DiscordConfig
        models_imported.append("DiscordConfig")
        print("✅ Discord models imported")
    except ImportError as e:
        print(f"⚠️  Discord models import error: {e}")
    
    try:
        # Wallet models - perbaiki import yang salah
        from app.domains.wallet.models.wallet import WalletTransaction, Transfer, TopUpRequest
        models_imported.extend(["WalletTransaction", "Transfer", "TopUpRequest"])
        print("✅ Wallet models imported")
    except ImportError as e:
        print(f"⚠️  Wallet models import error: {e}")
    
    try:
        # Admin models - import semua model admin
        from app.domains.admin.models.admin import Admin, AdminConfig, AdminAuditLog, AdminNotificationSetting
        models_imported.extend(["Admin", "AdminConfig", "AdminAuditLog", "AdminNotificationSetting"])
        print("✅ Admin models imported")
    except ImportError as e:
        print(f"⚠️  Admin models import error: {e}")
    
    try:
        # Product models
        from app.domains.product.models.product import Product
        models_imported.append("Product")
        print("✅ Product models imported")
    except ImportError as e:
        print(f"⚠️  Product models import error: {e}")
    
    try:
        # Auth/User models
        from app.domains.auth.models.user import User
        models_imported.append("User")
        print("✅ Auth/User models imported")
    except ImportError as e:
        print(f"⚠️  Auth/User models import error: {e}")
    
    try:
        # Voucher models - import semua model voucher
        from app.domains.voucher.models.voucher import Voucher, VoucherUsage
        models_imported.extend(["Voucher", "VoucherUsage"])
        print("✅ Voucher models imported")
    except ImportError as e:
        print(f"⚠️  Voucher models import error: {e}")
    
    try:
        # Analytics models - import semua model analytics
        from app.domains.analytics.models.analytics import AnalyticsEvent, ProductAnalytics, VoucherAnalytics, DashboardMetrics
        models_imported.extend(["AnalyticsEvent", "ProductAnalytics", "VoucherAnalytics", "DashboardMetrics"])
        print("✅ Analytics models imported")
    except ImportError as e:
        print(f"⚠️  Analytics models import error: {e}")
    
    try:
        # PPOB models - tambahkan model PPOB yang hilang
        from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, PPOBMarginConfig
        models_imported.extend(["PPOBTransaction", "PPOBProduct", "PPOBMarginConfig"])
        print("✅ PPOB models imported")
    except ImportError as e:
        print(f"⚠️  PPOB models import error: {e}")
    
    print(f"📊 Total models imported: {len(models_imported)}")
    for model in models_imported:
        print(f"   - {model}")
    
    return models_imported

def get_database_url():
    """Mendapatkan DATABASE_URL dari environment atau settings"""
    # Prioritas: Environment variable > Settings file
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        try:
            from app.infrastructure.config.settings import settings
            database_url = settings.DATABASE_URL
            print(f"📋 Using DATABASE_URL from settings: {database_url}")
        except ImportError:
            print("❌ Tidak bisa mengimpor settings")
            return None
    else:
        print(f"📋 Using DATABASE_URL from environment")
    
    return database_url

def create_tables_postgresql(engine):
    """Membuat tabel untuk PostgreSQL"""
    print("🐘 Creating tables for PostgreSQL...")
    
    try:
        from app.core.database import Base
        
        # Import semua models
        import_all_models()
        
        # Buat semua tabel
        Base.metadata.create_all(bind=engine)
        
        # Verifikasi tabel yang dibuat
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✅ Tables created successfully! Total: {len(tables)}")
        for table in tables:
            print(f"   - {table}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating PostgreSQL tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_tables_sqlite(engine):
    """Membuat tabel untuk SQLite"""
    print("🗃️  Creating tables for SQLite...")
    
    try:
        from app.core.database import Base
        
        # Import semua models
        import_all_models()
        
        # Buat semua tabel
        Base.metadata.create_all(bind=engine)
        
        # Verifikasi tabel yang dibuat
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✅ Tables created successfully! Total: {len(tables)}")
        for table in tables:
            print(f"   - {table}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating SQLite tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def auto_create_tables():
    """Auto-create tabel berdasarkan database yang digunakan"""
    print("🏗️  Starting auto-create tables...")
    
    # Dapatkan DATABASE_URL
    database_url = get_database_url()
    if not database_url:
        print("❌ DATABASE_URL tidak ditemukan")
        return False
    
    print(f"🔗 Database URL: {database_url[:50]}...")
    
    try:
        # Buat engine
        engine = create_engine(database_url)
        
        # Test koneksi
        with engine.connect() as connection:
            print("✅ Database connection successful")
        
        # Deteksi jenis database
        if "postgresql" in database_url:
            print("🐘 Detected PostgreSQL database")
            success = create_tables_postgresql(engine)
        elif "sqlite" in database_url:
            print("🗃️  Detected SQLite database")
            success = create_tables_sqlite(engine)
        else:
            print(f"⚠️  Unknown database type in URL: {database_url}")
            # Try generic approach
            success = create_tables_postgresql(engine)
        
        if success:
            print("🎉 Auto-create tables completed successfully!")
            return True
        else:
            print("❌ Auto-create tables failed")
            return False
            
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_existing_tables():
    """Mengecek tabel yang sudah ada"""
    print("\n🔍 Checking existing tables...")
    
    database_url = get_database_url()
    if not database_url:
        return False
    
    try:
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Existing tables ({len(tables)}):")
        if tables:
            for table in tables:
                # Get column info
                columns = inspector.get_columns(table)
                print(f"   📋 {table} ({len(columns)} columns)")
                for col in columns[:3]:  # Show first 3 columns
                    print(f"      - {col['name']} ({col['type']})")
                if len(columns) > 3:
                    print(f"      ... and {len(columns) - 3} more columns")
        else:
            print("   (No tables found)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 AUTO-CREATE TABLES FOR RAILWAY POSTGRESQL")
    print("=" * 60)
    
    # Check existing tables first
    check_existing_tables()
    
    # Auto-create tables
    success = auto_create_tables()
    
    if success:
        # Check tables again to see what was created
        print("\n" + "=" * 40)
        print("📊 FINAL TABLE STATUS")
        print("=" * 40)
        check_existing_tables()
        
        print("\n🎉 Auto-create tables process completed successfully!")
        return True
    else:
        print("\n❌ Auto-create tables process failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
