from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_sample_data():
    db = next(get_db())
    
    try:
        # Create sample admins
        admin_count = db.execute(text("SELECT COUNT(*) FROM admins")).scalar()
        if admin_count == 0:
            admin_pwd = pwd_context.hash("admin123")
            staff_pwd = pwd_context.hash("staff123")
            
            db.execute(text("""
                INSERT INTO admins (username, email, full_name, hashed_password, role, phone_number)
                VALUES 
                (:username1, :email1, :name1, :pwd1, :role1, :phone1),
                (:username2, :email2, :name2, :pwd2, :role2, :phone2)
            """), {
                'username1': 'admin', 'email1': 'admin@example.com', 'name1': 'Admin User',
                'pwd1': admin_pwd, 'role1': 'superadmin', 'phone1': '+6281234567890',
                'username2': 'staff1', 'email2': 'staff1@example.com', 'name2': 'Staff One',
                'pwd2': staff_pwd, 'role2': 'staff', 'phone2': '+6281234567891'
            })
            print("Created sample admins")

        # Create sample users
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if user_count == 0:
            user_pwd = pwd_context.hash("user123")
            
            db.execute(text("""
                INSERT INTO users (username, email, full_name, hashed_password, is_active, phone_number, balance)
                VALUES 
                (:username1, :email1, :name1, :pwd1, true, :phone1, :balance1),
                (:username2, :email2, :name2, :pwd2, true, :phone2, :balance2)
            """), {
                'username1': 'user1', 'email1': 'user1@example.com', 'name1': 'User One',
                'pwd1': user_pwd, 'phone1': '+6281234567893', 'balance1': 1000000,
                'username2': 'user2', 'email2': 'user2@example.com', 'name2': 'User Two',
                'pwd2': user_pwd, 'phone2': '+6281234567894', 'balance2': 500000
            })
            print("Created sample users")

        # Create sample products
        product_count = db.execute(text("SELECT COUNT(*) FROM ppob_products")).scalar()
        if product_count == 0:
            categories = db.execute(text("SELECT id, code FROM ppob_categories")).fetchall()
            category_map = {cat[1]: cat[0] for cat in categories}
            
            for cat_code, cat_id in category_map.items():
                if cat_code == 'pulsa':
                    db.execute(text("""
                        INSERT INTO ppob_products (category_id, product_code, product_name, description, price, admin_fee)
                        VALUES (:cat_id, 'TSEL10', 'Telkomsel 10K', 'Pulsa Telkomsel 10.000', 11000, 1000)
                    """), {'cat_id': cat_id})
                elif cat_code == 'data':
                    db.execute(text("""
                        INSERT INTO ppob_products (category_id, product_code, product_name, description, price, admin_fee)
                        VALUES (:cat_id, 'TSEL1GB', 'Telkomsel 1GB', 'Paket Data Telkomsel 1GB', 15000, 1000)
                    """), {'cat_id': cat_id})
                elif cat_code == 'pln':
                    db.execute(text("""
                        INSERT INTO ppob_products (category_id, product_code, product_name, description, price, admin_fee)
                        VALUES (:cat_id, 'PLN20', 'Token PLN 20K', 'Token Listrik 20.000', 21000, 1000)
                    """), {'cat_id': cat_id})
            
            print("Created sample products")

        db.commit()
        print("Sample data creation completed!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
