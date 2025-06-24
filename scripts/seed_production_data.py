"""
Script untuk seed database dengan data production real
Menghapus semua data dummy dan mengisi dengan data PPOB real
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.domains.auth.models.user import User
from app.domains.admin.models.admin import Admin
from app.domains.ppob.models.ppob import PPOBCategory, PPOBProduct, PPOBMarginConfig
from app.infrastructure.config.settings import settings
from passlib.context import CryptContext
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_admin_user(db: Session):
    """Buat admin user dengan credentials dari environment"""
    try:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.username == settings.ADMIN_USERNAME).first()
        if existing_admin:
            logger.info(f"Admin user {settings.ADMIN_USERNAME} already exists")
            return existing_admin
        
        # Create new admin
        from app.domains.admin.models.admin import AdminRole
        admin = Admin(
            username=settings.ADMIN_USERNAME,
            email="admin@fa-application.com",
            full_name="FA Application Administrator",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_active=True,
            role=AdminRole.SUPER_ADMIN
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        logger.info(f"Admin user created: {settings.ADMIN_USERNAME}")
        return admin
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
        raise

def create_ppob_categories(db: Session):
    """Buat kategori PPOB real"""
    categories_data = [
        {
            "name": "Pulsa & Data",
            "code": "PULSA",
            "description": "Pulsa dan paket data semua operator",
            "icon": "fas fa-mobile-alt"
        },
        {
            "name": "PLN",
            "code": "PLN",
            "description": "Token listrik PLN",
            "icon": "fas fa-bolt"
        },
        {
            "name": "PDAM",
            "code": "PDAM",
            "description": "Tagihan air PDAM",
            "icon": "fas fa-tint"
        },
        {
            "name": "Internet & TV",
            "code": "INTERNET",
            "description": "Tagihan internet dan TV kabel",
            "icon": "fas fa-wifi"
        },
        {
            "name": "Game Voucher",
            "code": "GAME",
            "description": "Voucher game online",
            "icon": "fas fa-gamepad"
        },
        {
            "name": "E-Wallet",
            "code": "EWALLET",
            "description": "Top up e-wallet",
            "icon": "fas fa-wallet"
        }
    ]
    
    created_categories = []
    
    for cat_data in categories_data:
        try:
            # Check if category exists
            existing = db.query(PPOBCategory).filter(PPOBCategory.code == cat_data["code"]).first()
            if existing:
                logger.info(f"Category {cat_data['code']} already exists")
                created_categories.append(existing)
                continue
            
            category = PPOBCategory(
                name=cat_data["name"],
                code=cat_data["code"],
                description=cat_data["description"],
                icon=cat_data["icon"],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(category)
            db.commit()
            db.refresh(category)
            
            created_categories.append(category)
            logger.info(f"Created category: {cat_data['name']}")
            
        except Exception as e:
            logger.error(f"Error creating category {cat_data['code']}: {e}")
            db.rollback()
            continue
    
    return created_categories

def create_ppob_products(db: Session, categories: list):
    """Buat produk PPOB real"""
    
    # Map categories by code for easy access
    cat_map = {cat.code: cat for cat in categories}
    
    products_data = [
        # Pulsa & Data
        {"category": "PULSA", "code": "TSEL5", "name": "Telkomsel 5K", "price": 6000, "admin_fee": 500},
        {"category": "PULSA", "code": "TSEL10", "name": "Telkomsel 10K", "price": 11000, "admin_fee": 500},
        {"category": "PULSA", "code": "TSEL20", "name": "Telkomsel 20K", "price": 21000, "admin_fee": 500},
        {"category": "PULSA", "code": "TSEL25", "name": "Telkomsel 25K", "price": 26000, "admin_fee": 500},
        {"category": "PULSA", "code": "TSEL50", "name": "Telkomsel 50K", "price": 51000, "admin_fee": 500},
        {"category": "PULSA", "code": "TSEL100", "name": "Telkomsel 100K", "price": 101000, "admin_fee": 500},
        
        {"category": "PULSA", "code": "ISAT5", "name": "Indosat 5K", "price": 5500, "admin_fee": 500},
        {"category": "PULSA", "code": "ISAT10", "name": "Indosat 10K", "price": 10500, "admin_fee": 500},
        {"category": "PULSA", "code": "ISAT25", "name": "Indosat 25K", "price": 25500, "admin_fee": 500},
        {"category": "PULSA", "code": "ISAT50", "name": "Indosat 50K", "price": 50500, "admin_fee": 500},
        
        {"category": "PULSA", "code": "XL5", "name": "XL 5K", "price": 5500, "admin_fee": 500},
        {"category": "PULSA", "code": "XL10", "name": "XL 10K", "price": 10500, "admin_fee": 500},
        {"category": "PULSA", "code": "XL25", "name": "XL 25K", "price": 25500, "admin_fee": 500},
        {"category": "PULSA", "code": "XL50", "name": "XL 50K", "price": 50500, "admin_fee": 500},
        
        # PLN
        {"category": "PLN", "code": "PLN20", "name": "PLN 20K", "price": 21000, "admin_fee": 1000},
        {"category": "PLN", "code": "PLN50", "name": "PLN 50K", "price": 51000, "admin_fee": 1000},
        {"category": "PLN", "code": "PLN100", "name": "PLN 100K", "price": 101000, "admin_fee": 1000},
        {"category": "PLN", "code": "PLN200", "name": "PLN 200K", "price": 201000, "admin_fee": 1000},
        {"category": "PLN", "code": "PLN500", "name": "PLN 500K", "price": 501000, "admin_fee": 1000},
        
        # Game Voucher
        {"category": "GAME", "code": "GARENA50", "name": "Garena 50 Shells", "price": 10000, "admin_fee": 500},
        {"category": "GAME", "code": "GARENA100", "name": "Garena 100 Shells", "price": 20000, "admin_fee": 500},
        {"category": "GAME", "code": "STEAM20", "name": "Steam Wallet 20K", "price": 22000, "admin_fee": 1000},
        {"category": "GAME", "code": "STEAM50", "name": "Steam Wallet 50K", "price": 52000, "admin_fee": 1000},
        {"category": "GAME", "code": "MLBB50", "name": "Mobile Legends 50 Diamond", "price": 15000, "admin_fee": 500},
        {"category": "GAME", "code": "MLBB100", "name": "Mobile Legends 100 Diamond", "price": 28000, "admin_fee": 500},
        
        # E-Wallet
        {"category": "EWALLET", "code": "GOPAY10", "name": "GoPay 10K", "price": 11000, "admin_fee": 500},
        {"category": "EWALLET", "code": "GOPAY25", "name": "GoPay 25K", "price": 26000, "admin_fee": 500},
        {"category": "EWALLET", "code": "GOPAY50", "name": "GoPay 50K", "price": 51000, "admin_fee": 500},
        {"category": "EWALLET", "code": "OVO10", "name": "OVO 10K", "price": 11000, "admin_fee": 500},
        {"category": "EWALLET", "code": "OVO25", "name": "OVO 25K", "price": 26000, "admin_fee": 500},
        {"category": "EWALLET", "code": "DANA10", "name": "DANA 10K", "price": 11000, "admin_fee": 500},
        {"category": "EWALLET", "code": "DANA25", "name": "DANA 25K", "price": 26000, "admin_fee": 500},
    ]
    
    created_products = []
    
    for prod_data in products_data:
        try:
            # Check if product exists
            existing = db.query(PPOBProduct).filter(PPOBProduct.product_code == prod_data["code"]).first()
            if existing:
                logger.info(f"Product {prod_data['code']} already exists")
                created_products.append(existing)
                continue
            
            category = cat_map.get(prod_data["category"])
            if not category:
                logger.warning(f"Category {prod_data['category']} not found for product {prod_data['code']}")
                continue
            
            product = PPOBProduct(
                category_id=category.id,
                product_code=prod_data["code"],
                product_name=prod_data["name"],
                description=f"Produk {prod_data['name']} - {category.name}",
                price=prod_data["price"],
                admin_fee=prod_data["admin_fee"],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            created_products.append(product)
            logger.info(f"Created product: {prod_data['name']}")
            
        except Exception as e:
            logger.error(f"Error creating product {prod_data['code']}: {e}")
            db.rollback()
            continue
    
    return created_products

def create_margin_configs(db: Session, categories: list):
    """Buat konfigurasi margin untuk setiap kategori"""
    
    margin_configs = [
        {"category": "PULSA", "margin_type": "percentage", "margin_value": 3.0},
        {"category": "PLN", "margin_type": "percentage", "margin_value": 2.5},
        {"category": "PDAM", "margin_type": "percentage", "margin_value": 2.0},
        {"category": "INTERNET", "margin_type": "percentage", "margin_value": 2.0},
        {"category": "GAME", "margin_type": "percentage", "margin_value": 5.0},
        {"category": "EWALLET", "margin_type": "percentage", "margin_value": 2.0},
    ]
    
    for margin_data in margin_configs:
        try:
            # Check if margin config exists
            existing = db.query(PPOBMarginConfig).filter(
                PPOBMarginConfig.category == margin_data["category"],
                PPOBMarginConfig.product_code.is_(None)
            ).first()
            
            if existing:
                logger.info(f"Margin config for {margin_data['category']} already exists")
                continue
            
            margin_config = PPOBMarginConfig(
                category=margin_data["category"],
                product_code=None,  # Global margin for category
                margin_type=margin_data["margin_type"],
                margin_value=margin_data["margin_value"],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(margin_config)
            db.commit()
            db.refresh(margin_config)
            
            logger.info(f"Created margin config for {margin_data['category']}: {margin_data['margin_value']}%")
            
        except Exception as e:
            logger.error(f"Error creating margin config for {margin_data['category']}: {e}")
            db.rollback()
            continue

def main():
    """Main function untuk seed database"""
    logger.info("🚀 Starting production data seeding...")
    
    try:
        # Create database tables
        from app.core.database import Base
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        
        # Get database session
        db = next(get_db())
        
        # 1. Create admin user
        logger.info("📝 Creating admin user...")
        admin = create_admin_user(db)
        
        # 2. Create PPOB categories
        logger.info("📂 Creating PPOB categories...")
        categories = create_ppob_categories(db)
        
        # 3. Create PPOB products
        logger.info("🛍️ Creating PPOB products...")
        products = create_ppob_products(db, categories)
        
        # 4. Create margin configurations
        logger.info("💰 Creating margin configurations...")
        create_margin_configs(db, categories)
        
        logger.info("🎯 Production data seeding completed successfully!")
        logger.info(f"✅ Created {len(categories)} categories")
        logger.info(f"✅ Created {len(products)} products")
        logger.info(f"✅ Admin user: {settings.ADMIN_USERNAME}")
        logger.info("🔐 Use the admin credentials from .env file to login")
        
    except Exception as e:
        logger.error(f"❌ Error during seeding: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
