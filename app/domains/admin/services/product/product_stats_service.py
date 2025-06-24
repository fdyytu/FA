from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Any

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import ProductManagementRepository
from app.domains.ppob.models.ppob import PPOBProduct


class ProductStatsService(BaseService):
    """Service untuk statistik produk - Single Responsibility: Product statistics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductManagementRepository(db)
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Ambil statistik umum produk"""
        total_products = self.db.query(PPOBProduct).count()
        active_products = self.db.query(PPOBProduct).filter(PPOBProduct.is_active == "1").count()
        inactive_products = total_products - active_products
        
        # Statistik per kategori
        category_stats = self.db.query(
            PPOBProduct.category,
            func.count(PPOBProduct.id).label('count')
        ).group_by(PPOBProduct.category).all()
        
        # Produk dengan harga tertinggi dan terendah
        highest_price_product = self.db.query(PPOBProduct).order_by(desc(PPOBProduct.price)).first()
        lowest_price_product = self.db.query(PPOBProduct).filter(PPOBProduct.price > 0).order_by(PPOBProduct.price).first()
        
        return {
            "total_products": total_products,
            "active_products": active_products,
            "inactive_products": inactive_products,
            "category_distribution": [
                {"category": stat.category, "count": stat.count}
                for stat in category_stats
            ],
            "price_range": {
                "highest": {
                    "product_name": highest_price_product.product_name if highest_price_product else None,
                    "price": float(highest_price_product.price) if highest_price_product else 0
                },
                "lowest": {
                    "product_name": lowest_price_product.product_name if lowest_price_product else None,
                    "price": float(lowest_price_product.price) if lowest_price_product else 0
                }
            }
        }
    
    def get_category_stats(self) -> List[Dict[str, Any]]:
        """Ambil statistik per kategori"""
        stats = self.db.query(
            PPOBProduct.category,
            func.count(PPOBProduct.id).label('total_products'),
            func.sum(func.case([(PPOBProduct.is_active == "1", 1)], else_=0)).label('active_products'),
            func.avg(PPOBProduct.price).label('avg_price'),
            func.min(PPOBProduct.price).label('min_price'),
            func.max(PPOBProduct.price).label('max_price')
        ).group_by(PPOBProduct.category).all()
        
        return [
            {
                "category": stat.category,
                "total_products": stat.total_products,
                "active_products": int(stat.active_products or 0),
                "inactive_products": stat.total_products - int(stat.active_products or 0),
                "avg_price": float(stat.avg_price or 0),
                "min_price": float(stat.min_price or 0),
                "max_price": float(stat.max_price or 0)
            }
            for stat in stats
        ]
    
    def get_price_distribution(self) -> Dict[str, int]:
        """Ambil distribusi harga produk"""
        # Kategorikan produk berdasarkan range harga
        price_ranges = {
            "0-10000": 0,
            "10001-50000": 0,
            "50001-100000": 0,
            "100001-500000": 0,
            "500000+": 0
        }
        
        products = self.db.query(PPOBProduct.price).all()
        
        for product in products:
            price = float(product.price)
            if price <= 10000:
                price_ranges["0-10000"] += 1
            elif price <= 50000:
                price_ranges["10001-50000"] += 1
            elif price <= 100000:
                price_ranges["50001-100000"] += 1
            elif price <= 500000:
                price_ranges["100001-500000"] += 1
            else:
                price_ranges["500000+"] += 1
        
        return price_ranges
