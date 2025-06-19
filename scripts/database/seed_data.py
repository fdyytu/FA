#!/usr/bin/env python3
"""
Script untuk menambahkan data sample PPOB products
"""
import sys
import os
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, PPOBProduct, PPOBCategory

def create_sample_products():
    """Buat sample products PPOB"""
    db = SessionLocal()
    
    try:
        # Create tables if not exist
        Base.metadata.create_all(bind=engine)
        
        # Sample products
        sample_products = [
            # Pulsa
            {
                "product_code": "PULSA_10K",
                "product_name": "Pulsa 10.000",
                "category": PPOBCategory.PULSA,
                "provider": "Telkomsel",
                "price": Decimal("10000"),
                "admin_fee": Decimal("1000"),
                "description": "Pulsa Telkomsel 10.000"
            },
            {
                "product_code": "PULSA_25K",
                "product_name": "Pulsa 25.000",
                "category": PPOBCategory.PULSA,
                "provider": "Telkomsel",
                "price": Decimal("25000"),
                "admin_fee": Decimal("1500"),
                "description": "Pulsa Telkomsel 25.000"
            },
            {
                "product_code": "PULSA_50K",
                "product_name": "Pulsa 50.000",
                "category": PPOBCategory.PULSA,
                "provider": "Telkomsel",
                "price": Decimal("50000"),
                "admin_fee": Decimal("2000"),
                "description": "Pulsa Telkomsel 50.000"
            },
            
            # Listrik
            {
                "product_code": "PLN_20K",
                "product_name": "Token PLN 20.000",
                "category": PPOBCategory.LISTRIK,
                "provider": "PLN",
                "price": Decimal("20000"),
                "admin_fee": Decimal("2500"),
                "description": "Token Listrik PLN 20.000"
            },
            {
                "product_code": "PLN_50K",
                "product_name": "Token PLN 50.000",
                "category": PPOBCategory.LISTRIK,
                "provider": "PLN",
                "price": Decimal("50000"),
                "admin_fee": Decimal("2500"),
                "description": "Token Listrik PLN 50.000"
            },
            {
                "product_code": "PLN_100K",
                "product_name": "Token PLN 100.000",
                "category": PPOBCategory.LISTRIK,
                "provider": "PLN",
                "price": Decimal("100000"),
                "admin_fee": Decimal("2500"),
                "description": "Token Listrik PLN 100.000"
            },
            
            # PDAM
            {
                "product_code": "PDAM_JKT",
                "product_name": "PDAM Jakarta",
                "category": PPOBCategory.PDAM,
                "provider": "PDAM Jakarta",
                "price": Decimal("0"),  # Harga akan ditentukan saat inquiry
                "admin_fee": Decimal("2500"),
                "description": "Pembayaran PDAM Jakarta"
            }
        ]
        
        # Check if products already exist
        existing_count = db.query(PPOBProduct).count()
        if existing_count > 0:
            print(f"Products already exist ({existing_count} products found). Skipping...")
            return
        
        # Add products
        for product_data in sample_products:
            product = PPOBProduct(**product_data)
            db.add(product)
        
        db.commit()
        print(f"Successfully added {len(sample_products)} sample products!")
        
        # Display added products
        products = db.query(PPOBProduct).all()
        print("\nAdded products:")
        for product in products:
            print(f"- {product.product_name} ({product.product_code}) - Rp {product.price:,}")
            
    except Exception as e:
        db.rollback()
        print(f"Error adding sample products: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding sample PPOB products...")
    create_sample_products()
