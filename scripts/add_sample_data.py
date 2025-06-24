"""
Script untuk menambahkan sample data (users dan transactions) 
untuk membuat dashboard lebih menarik dengan data real
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.auth.models.user import User
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, TransactionStatus
from passlib.context import CryptContext
import logging
from datetime import datetime, timedelta
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_sample_users(db: Session, count: int = 10):
    """Buat sample users"""
    created_users = []
    
    for i in range(1, count + 1):
        try:
            # Check if user exists
            username = f"user{i:03d}"
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                created_users.append(existing)
                continue
            
            user = User(
                username=username,
                email=f"user{i:03d}@example.com",
                full_name=f"Sample User {i:03d}",
                hashed_password=hash_password("password123"),
                is_active=True,
                phone_number=f"08123456{i:04d}",
                balance=random.randint(50000, 500000)
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            created_users.append(user)
            logger.info(f"Created user: {username}")
            
        except Exception as e:
            logger.error(f"Error creating user {i}: {e}")
            db.rollback()
            continue
    
    return created_users

def create_sample_transactions(db: Session, users: list, count: int = 50):
    """Buat sample transactions"""
    
    # Get available products
    products = db.query(PPOBProduct).filter(PPOBProduct.is_active == True).all()
    if not products:
        logger.warning("No products available for creating transactions")
        return []
    
    created_transactions = []
    statuses = [TransactionStatus.SUCCESS, TransactionStatus.PENDING, TransactionStatus.FAILED]
    status_weights = [0.7, 0.2, 0.1]  # 70% success, 20% pending, 10% failed
    
    for i in range(1, count + 1):
        try:
            # Random user and product
            user = random.choice(users)
            product = random.choice(products)
            
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            # Random status based on weights
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Generate transaction code
            transaction_code = f"TRX{created_at.strftime('%Y%m%d')}{i:04d}"
            
            # Check if transaction exists
            existing = db.query(PPOBTransaction).filter(
                PPOBTransaction.transaction_code == transaction_code
            ).first()
            if existing:
                continue
            
            # Random customer number (phone number format)
            customer_number = f"08{random.randint(1000000000, 9999999999)}"
            
            transaction = PPOBTransaction(
                user_id=user.id,
                transaction_code=transaction_code,
                category_id=product.category_id,
                product_code=product.product_code,
                product_name=product.product_name,
                customer_number=customer_number,
                customer_name=f"Customer {random.randint(1000, 9999)}",
                amount=product.price,
                admin_fee=product.admin_fee,
                total_amount=product.price + product.admin_fee,
                status=status,
                provider_ref=f"REF{random.randint(100000, 999999)}" if status == TransactionStatus.SUCCESS else None,
                notes=f"Transaction for {product.product_name}",
                created_at=created_at,
                updated_at=created_at
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(transaction)
            
            created_transactions.append(transaction)
            
            if i % 10 == 0:
                logger.info(f"Created {i} transactions...")
                
        except Exception as e:
            logger.error(f"Error creating transaction {i}: {e}")
            db.rollback()
            continue
    
    logger.info(f"Created {len(created_transactions)} transactions")
    return created_transactions

def update_user_activity(db: Session, users: list):
    """Update user activity status"""
    
    # Mark 80% of users as active (logged in recently)
    active_count = int(len(users) * 0.8)
    active_users = random.sample(users, active_count)
    
    for user in active_users:
        try:
            # Update last login to recent date
            days_ago = random.randint(0, 7)
            user.updated_at = datetime.utcnow() - timedelta(days=days_ago)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating user {user.username}: {e}")
            db.rollback()
            continue
    
    logger.info(f"Updated activity for {len(active_users)} users")

def main():
    """Main function untuk menambahkan sample data"""
    logger.info("🚀 Starting sample data creation...")
    
    try:
        # Get database session
        db = next(get_db())
        
        # 1. Create sample users
        logger.info("👥 Creating sample users...")
        users = create_sample_users(db, count=25)
        
        # 2. Create sample transactions
        logger.info("💳 Creating sample transactions...")
        transactions = create_sample_transactions(db, users, count=100)
        
        # 3. Update user activity
        logger.info("🔄 Updating user activity...")
        update_user_activity(db, users)
        
        logger.info("🎯 Sample data creation completed successfully!")
        logger.info(f"✅ Created {len(users)} users")
        logger.info(f"✅ Created {len(transactions)} transactions")
        
        # Show some statistics
        success_count = len([t for t in transactions if t.status == TransactionStatus.SUCCESS])
        pending_count = len([t for t in transactions if t.status == TransactionStatus.PENDING])
        failed_count = len([t for t in transactions if t.status == TransactionStatus.FAILED])
        
        total_revenue = sum([t.total_amount for t in transactions if t.status == TransactionStatus.SUCCESS])
        
        logger.info(f"📊 Transaction Statistics:")
        logger.info(f"   - Success: {success_count}")
        logger.info(f"   - Pending: {pending_count}")
        logger.info(f"   - Failed: {failed_count}")
        logger.info(f"   - Total Revenue: Rp {total_revenue:,.0f}")
        
    except Exception as e:
        logger.error(f"❌ Error during sample data creation: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
