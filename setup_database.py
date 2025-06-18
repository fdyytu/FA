import os
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    """Setup PostgreSQL database and tables"""
    try:
        # Create database if not exists
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'ppob_db'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE ppob_db")
            print("Database ppob_db created successfully")
        
        cur.close()
        conn.close()
        
        # Connect to ppob_db
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres",
            database="ppob_db"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Create admins table first
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT true,
                role VARCHAR(50) DEFAULT 'admin',
                phone_number VARCHAR(20),
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT true,
                is_superuser BOOLEAN DEFAULT false,
                phone_number VARCHAR(20),
                balance DECIMAL(15,2) DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create other tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ppob_categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL,
                code VARCHAR UNIQUE NOT NULL,
                description TEXT,
                icon VARCHAR,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ppob_products (
                id SERIAL PRIMARY KEY,
                category_id INTEGER REFERENCES ppob_categories(id),
                product_code VARCHAR UNIQUE NOT NULL,
                product_name VARCHAR NOT NULL,
                description TEXT,
                price DECIMAL(15,2) NOT NULL,
                admin_fee DECIMAL(15,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transaction status enum if not exists
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transaction_status') THEN
                    CREATE TYPE transaction_status AS ENUM ('PENDING', 'SUCCESS', 'FAILED', 'EXPIRED', 'REFUNDED', 'CANCELLED');
                END IF;
            END$$;
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ppob_transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                transaction_code VARCHAR UNIQUE,
                category_id INTEGER REFERENCES ppob_categories(id),
                product_code VARCHAR,
                product_name VARCHAR,
                customer_number VARCHAR,
                customer_name VARCHAR,
                amount DOUBLE PRECISION,
                admin_fee DOUBLE PRECISION DEFAULT 0,
                total_amount DOUBLE PRECISION,
                status transaction_status DEFAULT 'PENDING',
                provider_ref VARCHAR,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default categories if not exist
        categories = [
            ('Pulsa', 'pulsa', 'Pulsa All Operator'),
            ('Paket Data', 'data', 'Paket Data All Operator'),
            ('PLN', 'pln', 'Token Listrik PLN')
        ]
        
        for name, code, desc in categories:
            cur.execute("""
                INSERT INTO ppob_categories (name, code, description)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM ppob_categories WHERE code = %s
                )
            """, (name, code, desc, code))
        
        print("Tables created and default data inserted successfully")
        
        cur.close()
        conn.close()
        
        # Run alembic migrations with PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = "/project/sandbox/user-workspace:" + env.get("PYTHONPATH", "")
        subprocess.run(["alembic", "upgrade", "head"], env=env, check=True)
        print("Alembic migrations completed successfully")
        
        return True
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        return False

if __name__ == "__main__":
    setup_database()
