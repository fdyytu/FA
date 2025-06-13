#!/usr/bin/env python3
"""
Script untuk generate SECRET_KEY yang aman untuk Railway deployment.
Jalankan script ini untuk mendapatkan SECRET_KEY yang kuat.
"""

import secrets
import string

def generate_secret_key(length=64):
    """Generate a cryptographically strong secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_multiple_keys():
    """Generate multiple keys untuk berbagai keperluan."""
    print("🔐 SECRET KEY GENERATOR untuk Railway Deployment")
    print("=" * 60)
    
    print("\n1. SECRET_KEY (untuk JWT dan session):")
    secret_key = generate_secret_key(64)
    print(f"   {secret_key}")
    
    print("\n2. ADMIN_PASSWORD (untuk admin login):")
    admin_password = generate_secret_key(16)
    print(f"   {admin_password}")
    
    print("\n3. Database Password (jika manual setup):")
    db_password = generate_secret_key(20)
    print(f"   {db_password}")
    
    print("\n" + "=" * 60)
    print("📋 Copy environment variables ini ke Railway Dashboard:")
    print("=" * 60)
    print(f"SECRET_KEY={secret_key}")
    print(f"ADMIN_PASSWORD={admin_password}")
    print("ALGORITHM=HS256")
    print("ACCESS_TOKEN_EXPIRE_MINUTES=30")
    print("DEBUG=False")
    print("ENVIRONMENT=production")
    
    print("\n⚠️  PENTING:")
    print("- Jangan share SECRET_KEY ini dengan siapa pun")
    print("- Simpan ADMIN_PASSWORD dengan aman")
    print("- Gunakan password manager untuk menyimpan credentials")

if __name__ == "__main__":
    generate_multiple_keys()
