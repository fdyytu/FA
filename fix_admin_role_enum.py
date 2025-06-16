#!/usr/bin/env python3
"""
Script untuk memperbaiki nilai enum admin role di database
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def fix_admin_role_enum():
    """Perbaiki nilai enum admin role di database"""
    try:
        from app.core.database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            print("🔧 Memeriksa dan memperbaiki nilai enum admin role...")
            
            # Cek data admin yang ada
            result = db.execute(text("SELECT id, username, role FROM admins"))
            admins = result.fetchall()
            
            if not admins:
                print("ℹ️  Tidak ada data admin di database")
                return True
            
            print(f"📊 Ditemukan {len(admins)} admin:")
            
            # Mapping nilai lama ke nilai baru
            role_mapping = {
                'super_admin': 'SUPER_ADMIN',
                'admin': 'ADMIN', 
                'operator': 'OPERATOR'
            }
            
            updated_count = 0
            for admin in admins:
                admin_id, username, current_role = admin
                print(f"  - {username}: {current_role}")
                
                # Jika role menggunakan lowercase, update ke uppercase
                if current_role in role_mapping:
                    new_role = role_mapping[current_role]
                    print(f"    🔄 Mengupdate {current_role} -> {new_role}")
                    
                    update_sql = text("UPDATE admins SET role = :new_role WHERE id = :admin_id")
                    db.execute(update_sql, {
                        'new_role': new_role,
                        'admin_id': admin_id
                    })
                    updated_count += 1
                else:
                    print(f"    ✅ Role sudah benar: {current_role}")
            
            if updated_count > 0:
                db.commit()
                print(f"✅ Berhasil mengupdate {updated_count} admin role")
            else:
                print("✅ Semua admin role sudah benar")
            
            return True
            
        except Exception as e:
            print(f"❌ Database Error: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Memperbaiki enum admin role...")
    success = fix_admin_role_enum()
    if success:
        print("\n🎉 Perbaikan enum berhasil!")
    else:
        print("\n❌ Perbaikan enum gagal!")
