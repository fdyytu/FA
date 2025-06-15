#!/usr/bin/env python3
"""
Test admin login sederhana
"""
import sys
import os
from pathlib import Path
import requests
import json

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_admin_login():
    """Test login admin"""
    try:
        from app.core.database import SessionLocal
        from app.infrastructure.security.password_handler import PasswordHandler
        from sqlalchemy import Column, String, Text, Boolean, Enum
        import enum
        
        # Test database connection
        db = SessionLocal()
        
        # Query admin dari database
        from sqlalchemy import text
        result = db.execute(text("SELECT * FROM admins WHERE username = 'admin'"))
        admin_row = result.fetchone()
        
        if admin_row:
            print("✅ Admin ditemukan di database!")
            print(f"Username: {admin_row[1]}")  # username column
            print(f"Email: {admin_row[2]}")     # email column
            
            # Test password verification
            password_handler = PasswordHandler()
            stored_hash = admin_row[4]  # hashed_password column
            
            if password_handler.verify_password("admin123", stored_hash):
                print("✅ Password verification berhasil!")
                
                # Test API login
                print("\n🔄 Testing API login...")
                
                login_data = {
                    "username": "admin",
                    "password": "admin123"
                }
                
                response = requests.post(
                    "http://2aed62ec2240b28683.blackbx.ai/api/v1/admin/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    print("✅ API Login berhasil!")
                    data = response.json()
                    if "access_token" in data:
                        print(f"Access Token: {data['access_token'][:50]}...")
                else:
                    print("❌ API Login gagal!")
                    
            else:
                print("❌ Password verification gagal!")
        else:
            print("❌ Admin tidak ditemukan di database!")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing admin login...")
    test_admin_login()
