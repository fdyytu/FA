"""
Script sederhana untuk menampilkan data produk gaming yang akan di-seed
"""

def display_game_categories():
    """Tampilkan kategori game populer"""
    categories = [
        {"name": "Mobile Legends", "code": "ML", "icon": "🎮"},
        {"name": "Free Fire", "code": "FF", "icon": "🔥"},
        {"name": "PUBG Mobile", "code": "PUBG", "icon": "🎯"},
        {"name": "Genshin Impact", "code": "GENSHIN", "icon": "⚔️"},
        {"name": "Valorant", "code": "VALORANT", "icon": "🎪"}
    ]
    return categories

def display_game_products():
    """Tampilkan produk game"""
    products = [
        # Mobile Legends
        {"category": "ML", "name": "86 Diamond", "code": "ML_86", "price": 20000, "cost": 18000},
        {"category": "ML", "name": "172 Diamond", "code": "ML_172", "price": 40000, "cost": 36000},
        {"category": "ML", "name": "257 Diamond", "code": "ML_257", "price": 60000, "cost": 54000},
        {"category": "ML", "name": "344 Diamond", "code": "ML_344", "price": 80000, "cost": 72000},
        {"category": "ML", "name": "429 Diamond", "code": "ML_429", "price": 100000, "cost": 90000},
        
        # Free Fire
        {"category": "FF", "name": "70 Diamond", "code": "FF_70", "price": 10000, "cost": 9000},
        {"category": "FF", "name": "140 Diamond", "code": "FF_140", "price": 20000, "cost": 18000},
        {"category": "FF", "name": "355 Diamond", "code": "FF_355", "price": 50000, "cost": 45000},
        {"category": "FF", "name": "720 Diamond", "code": "FF_720", "price": 100000, "cost": 90000},
        
        # PUBG Mobile
        {"category": "PUBG", "name": "60 UC", "code": "PUBG_60", "price": 15000, "cost": 13500},
        {"category": "PUBG", "name": "325 UC", "code": "PUBG_325", "price": 75000, "cost": 67500},
        {"category": "PUBG", "name": "660 UC", "code": "PUBG_660", "price": 150000, "cost": 135000},
        
        # Genshin Impact
        {"category": "GENSHIN", "name": "60 Genesis Crystal", "code": "GI_60", "price": 15000, "cost": 13500},
        {"category": "GENSHIN", "name": "330 Genesis Crystal", "code": "GI_330", "price": 75000, "cost": 67500},
        {"category": "GENSHIN", "name": "1090 Genesis Crystal", "code": "GI_1090", "price": 250000, "cost": 225000},
    ]
    return products

def main():
    """Main function untuk menampilkan data"""
    print("🎮 DATA PRODUK GAMING YANG AKAN DI-IMPLEMENTASIKAN")
    print("=" * 60)
    
    categories = display_game_categories()
    products = display_game_products()
    
    print(f"\n📋 KATEGORI GAME ({len(categories)} kategori):")
    for cat in categories:
        print(f"  {cat['icon']} {cat['name']} ({cat['code']})")
    
    print(f"\n🎯 PRODUK GAME ({len(products)} produk):")
    current_category = ""
    for prod in products:
        if prod['category'] != current_category:
            current_category = prod['category']
            print(f"\n  📱 {current_category}:")
        
        margin = ((prod['price'] - prod['cost']) / prod['cost']) * 100
        print(f"    • {prod['name']}: Rp {prod['price']:,} (margin {margin:.1f}%)")
    
    print(f"\n💰 TOTAL REVENUE POTENTIAL:")
    total_products = len(products)
    avg_price = sum(p['price'] for p in products) / len(products)
    print(f"  • Total Produk: {total_products}")
    print(f"  • Harga Rata-rata: Rp {avg_price:,.0f}")
    print(f"  • Estimasi Revenue/hari (100 transaksi): Rp {avg_price * 100:,.0f}")

if __name__ == "__main__":
    main()
