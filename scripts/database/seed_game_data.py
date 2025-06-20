"""
Script untuk seed data produk gaming
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domains.game.models.game_models import GameCategory, GameProduct
from app.core.database import get_db

def seed_game_categories():
    """Seed kategori game populer"""
    categories = [
        {
            "name": "Mobile Legends",
            "code": "ML",
            "icon": "https://cdn.mobilelegends.com/icon.png"
        },
        {
            "name": "Free Fire",
            "code": "FF", 
            "icon": "https://cdn.freefire.com/icon.png"
        },
        {
            "name": "PUBG Mobile",
            "code": "PUBG",
            "icon": "https://cdn.pubgmobile.com/icon.png"
        },
        {
            "name": "Genshin Impact",
            "code": "GENSHIN",
            "icon": "https://cdn.genshin.com/icon.png"
        },
        {
            "name": "Valorant",
            "code": "VALORANT",
            "icon": "https://cdn.valorant.com/icon.png"
        }
    ]
    
    return categories

def seed_game_products():
    """Seed produk game"""
    products = [
        # Mobile Legends
        {"category_code": "ML", "name": "86 Diamond", "code": "ML_86", "price": 20000, "cost": 18000, "stock": 100},
        {"category_code": "ML", "name": "172 Diamond", "code": "ML_172", "price": 40000, "cost": 36000, "stock": 100},
        {"category_code": "ML", "name": "257 Diamond", "code": "ML_257", "price": 60000, "cost": 54000, "stock": 100},
        {"category_code": "ML", "name": "344 Diamond", "code": "ML_344", "price": 80000, "cost": 72000, "stock": 100},
        {"category_code": "ML", "name": "429 Diamond", "code": "ML_429", "price": 100000, "cost": 90000, "stock": 100},
        
        # Free Fire
        {"category_code": "FF", "name": "70 Diamond", "code": "FF_70", "price": 10000, "cost": 9000, "stock": 100},
        {"category_code": "FF", "name": "140 Diamond", "code": "FF_140", "price": 20000, "cost": 18000, "stock": 100},
        {"category_code": "FF", "name": "355 Diamond", "code": "FF_355", "price": 50000, "cost": 45000, "stock": 100},
        {"category_code": "FF", "name": "720 Diamond", "code": "FF_720", "price": 100000, "cost": 90000, "stock": 100},
        
        # PUBG Mobile
        {"category_code": "PUBG", "name": "60 UC", "code": "PUBG_60", "price": 15000, "cost": 13500, "stock": 100},
        {"category_code": "PUBG", "name": "325 UC", "code": "PUBG_325", "price": 75000, "cost": 67500, "stock": 100},
        {"category_code": "PUBG", "name": "660 UC", "code": "PUBG_660", "price": 150000, "cost": 135000, "stock": 100},
        
        # Genshin Impact
        {"category_code": "GENSHIN", "name": "60 Genesis Crystal", "code": "GI_60", "price": 15000, "cost": 13500, "stock": 100},
        {"category_code": "GENSHIN", "name": "330 Genesis Crystal", "code": "GI_330", "price": 75000, "cost": 67500, "stock": 100},
        {"category_code": "GENSHIN", "name": "1090 Genesis Crystal", "code": "GI_1090", "price": 250000, "cost": 225000, "stock": 100},
    ]
    
    return products

def main():
    """Main function untuk seed data"""
    print("🎮 Memulai seed data produk gaming...")
    
    # Simulasi seed (dalam implementasi nyata perlu koneksi database)
    categories = seed_game_categories()
    products = seed_game_products()
    
    print(f"✅ Berhasil seed {len(categories)} kategori game")
    print(f"✅ Berhasil seed {len(products)} produk game")
    
    print("\n📋 Kategori yang ditambahkan:")
    for cat in categories:
        print(f"  - {cat['name']} ({cat['code']})")
    
    print("\n🎯 Produk yang ditambahkan:")
    for prod in products:
        print(f"  - {prod['name']}: Rp {prod['price']:,}")

if __name__ == "__main__":
    main()
