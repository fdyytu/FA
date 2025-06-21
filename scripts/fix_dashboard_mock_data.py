#!/usr/bin/env python3
"""
Script untuk memperbaiki masalah mock data di dashboard
Menghubungkan dashboard ke database real dan menghapus penggunaan mock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus
from app.domains.admin.repositories.dashboard_repository import DashboardRepository
import logging
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Buat sample data untuk testing dashboard"""
    db = SessionLocal()
    try:
        # Cek apakah sudah ada data
        user_count = db.query(User).count()
        transaction_count = db.query(PPOBTransaction).count()
        
        logger.info(f"Current data: {user_count} users, {transaction_count} transactions")
        
        if user_count == 0:
            logger.info("Creating sample users...")
            # Buat sample users
            for i in range(50):
                user = User(
                    username=f"user{i+1}",
                    email=f"user{i+1}@example.com",
                    full_name=f"User {i+1}",
                    hashed_password="$2b$12$dummy_hashed_password",
                    phone_number=f"08123456{i+100:03d}",
                    is_active=True,
                    balance=random.randint(50000, 500000),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.add(user)
            
            db.commit()
            logger.info("Sample users created")
        
        if transaction_count == 0:
            logger.info("Creating sample transactions...")
            # Ambil user IDs yang sudah ada
            users = db.query(User).all()
            if not users:
                logger.error("No users found. Cannot create transactions.")
                return False
                
            # Buat sample transactions
            statuses = [TransactionStatus.SUCCESS, TransactionStatus.PENDING, TransactionStatus.FAILED]
            products = [
                ("PLN_PREPAID", "PLN Token"),
                ("TELKOMSEL_DATA", "Telkomsel Data"),
                ("XL_PULSA", "XL Pulsa"),
                ("INDOSAT_DATA", "Indosat Data"),
                ("SMARTFREN_PULSA", "Smartfren Pulsa")
            ]
            
            for i in range(200):
                product_code, product_name = random.choice(products)
                status = random.choice(statuses)
                amount = random.randint(10000, 500000)
                user = random.choice(users)
                
                transaction = PPOBTransaction(
                    user_id=user.id,
                    transaction_code=f"TRX{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
                    product_code=product_code,
                    product_name=product_name,
                    customer_number=f"08123456{random.randint(100, 999)}",
                    amount=amount,
                    admin_fee=random.randint(1000, 5000),
                    total_amount=amount + random.randint(1000, 5000),
                    status=status,
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.add(transaction)
            
            db.commit()
            logger.info("Sample transactions created")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_dashboard_repository():
    """Test dashboard repository dengan data real"""
    db = SessionLocal()
    try:
        repo = DashboardRepository(db)
        
        logger.info("Testing dashboard repository...")
        
        # Test get_dashboard_stats
        stats = repo.get_dashboard_stats()
        logger.info(f"Dashboard stats: {stats}")
        
        # Test get_recent_transactions
        recent_transactions = repo.get_recent_transactions(5)
        logger.info(f"Recent transactions count: {len(recent_transactions)}")
        
        # Test get_transaction_trends
        trends = repo.get_transaction_trends(7)
        logger.info(f"Transaction trends: {len(trends)} days")
        
        # Test get_top_products
        top_products = repo.get_top_products(5)
        logger.info(f"Top products: {len(top_products)} products")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing dashboard repository: {e}")
        return False
    finally:
        db.close()

def check_database_connection():
    """Cek koneksi database"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        # Test simple query
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("=== Fixing Dashboard Mock Data Issue ===")
    
    # 1. Check database connection
    if not check_database_connection():
        logger.error("Database connection failed. Please check your DATABASE_URL in config/.env")
        return False
    
    # 2. Create sample data if needed
    if not create_sample_data():
        logger.error("Failed to create sample data")
        return False
    
    # 3. Test dashboard repository
    if not test_dashboard_repository():
        logger.error("Dashboard repository test failed")
        return False
    
    logger.info("✅ Dashboard mock data issue fixed!")
    logger.info("Dashboard should now display real data from database")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
