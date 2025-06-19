#!/usr/bin/env python3
"""
Script sederhana untuk cek status database
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 50)
print("🔍 CEK STATUS DATABASE")
print("=" * 50)

database_url = os.getenv('DATABASE_URL')

if database_url:
    if 'postgresql' in database_url:
        print("✅ PostgreSQL Railway TERKONEKSI")
        print(f"🔗 URL: {database_url[:50]}...")
    elif 'sqlite' in database_url:
        print("⚠️  Menggunakan SQLite (development)")
        print(f"📁 File: {database_url}")
    else:
        print(f"❓ Database type tidak dikenal: {database_url}")
else:
    print("❌ DATABASE_URL tidak ditemukan")
    print("💡 PostgreSQL Railway belum dikonfigurasi")
    print()
    print("🚀 LANGKAH SETUP:")
    print("1. Buka Railway dashboard")
    print("2. Add Service → Database → PostgreSQL")
    print("3. Tunggu hingga DATABASE_URL muncul")
    print("4. Restart aplikasi")

print("=" * 50)
