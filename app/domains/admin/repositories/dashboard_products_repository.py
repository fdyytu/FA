"""
Dashboard Products Repository
Repository untuk data produk dashboard
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
import logging

from app.domains.ppob.models.ppob import PPOBProduct, PPOBTransaction, PPOBCategory
from app.common.base_classes.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DashboardProductsRepository(BaseRepository):
    """Repository untuk data produk dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_top_products(self, limit: int = 5) -> Dict[str, Any]:
        """Ambil produk terlaris"""
        try:
            # Query untuk mendapatkan produk dengan transaksi terbanyak
            product_stats = self.db.query(
                PPOBProduct.id,
                PPOBProduct.name,
                PPOBProduct.price,
                PPOBProduct.category_id,
                func.count(PPOBTransaction.id).label('transaction_count'),
                func.sum(PPOBTransaction.amount).label('total_revenue')
            ).join(
                PPOBTransaction, PPOBProduct.id == PPOBTransaction.product_id, isouter=True
            ).group_by(
                PPOBProduct.id, PPOBProduct.name, PPOBProduct.price, PPOBProduct.category_id
            ).order_by(
                desc('transaction_count')
            ).limit(limit).all()
            
            result = []
            for product in product_stats:
                try:
                    # Get category name
                    category_name = "Unknown"
                    if product.category_id:
                        category = self.db.query(PPOBCategory).filter(
                            PPOBCategory.id == product.category_id
                        ).first()
                        if category:
                            category_name = category.name
                    
                    product_data = {
                        "id": product.id,
                        "name": product.name,
                        "price": float(product.price) if product.price else 0,
                        "category": category_name,
                        "transaction_count": product.transaction_count or 0,
                        "total_revenue": float(product.total_revenue) if product.total_revenue else 0
                    }
                    result.append(product_data)
                except Exception as product_error:
                    logger.warning(f"Error processing product {product.id}: {product_error}")
                    continue
            
            return {
                "top_products": result,
                "total_products_analyzed": len(result)
            }
            
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return {
                "top_products": [],
                "total_products_analyzed": 0
            }
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Ambil statistik produk"""
        try:
            total_products = self.db.query(PPOBProduct).count()
            active_products = self.db.query(PPOBProduct).filter(
                PPOBProduct.is_active == True
            ).count()
            
            # Get products by category
            category_stats = self.db.query(
                PPOBCategory.name,
                func.count(PPOBProduct.id).label('product_count')
            ).join(
                PPOBProduct, PPOBCategory.id == PPOBProduct.category_id, isouter=True
            ).group_by(
                PPOBCategory.name
            ).all()
            
            categories = {}
            for cat in category_stats:
                categories[cat.name] = cat.product_count or 0
            
            return {
                "total_products": total_products,
                "active_products": active_products,
                "inactive_products": total_products - active_products,
                "products_by_category": categories
            }
            
        except Exception as e:
            logger.error(f"Error getting product stats: {e}")
            return {
                "total_products": 0,
                "active_products": 0,
                "inactive_products": 0,
                "products_by_category": {}
            }
