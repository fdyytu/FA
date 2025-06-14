from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, text
from datetime import datetime
from app.domains.product.models.product import Product, Voucher, VoucherUsage
from app.domains.product.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductFilter,
    VoucherCreate, VoucherUpdate, VoucherFilter
)
from app.shared.base_classes.base_repository import BaseRepository
import json
import logging

logger = logging.getLogger(__name__)

class ProductRepository(BaseRepository[Product]):
    """
    Repository untuk menangani operasi database produk.
    Mengimplementasikan Repository Pattern untuk abstraksi data access.
    """
    
    def __init__(self, db: Session):
        super().__init__(Product, db)
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """Membuat produk baru"""
        try:
            # Convert lists to JSON strings
            tags_json = json.dumps(product_data.tags) if product_data.tags else None
            gallery_images_json = json.dumps(product_data.gallery_images) if product_data.gallery_images else None
            
            db_product = Product(
                name=product_data.name,
                slug=product_data.slug,
                description=product_data.description,
                short_description=product_data.short_description,
                category=product_data.category,
                subcategory=product_data.subcategory,
                tags=tags_json,
                price=product_data.price,
                cost_price=product_data.cost_price,
                compare_at_price=product_data.compare_at_price,
                sku=product_data.sku,
                stock_quantity=product_data.stock_quantity,
                track_inventory=product_data.track_inventory,
                allow_backorder=product_data.allow_backorder,
                weight=product_data.weight,
                dimensions=product_data.dimensions,
                meta_title=product_data.meta_title,
                meta_description=product_data.meta_description,
                featured_image=product_data.featured_image,
                gallery_images=gallery_images_json,
                is_featured=product_data.is_featured,
                is_digital=product_data.is_digital,
                requires_shipping=product_data.requires_shipping
            )
            
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            
            logger.info(f"Product created: {product_data.name}")
            return db_product
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            self.db.rollback()
            raise
    
    def get_products_by_filter(self, filter_params: ProductFilter, 
                              limit: int = 20, offset: int = 0) -> List[Product]:
        """Mendapatkan produk berdasarkan filter"""
        try:
            query = self.db.query(Product)
            
            # Apply filters
            if filter_params.category:
                query = query.filter(Product.category == filter_params.category)
            
            if filter_params.subcategory:
                query = query.filter(Product.subcategory == filter_params.subcategory)
            
            if filter_params.min_price is not None:
                query = query.filter(Product.price >= filter_params.min_price)
            
            if filter_params.max_price is not None:
                query = query.filter(Product.price <= filter_params.max_price)
            
            if filter_params.is_featured is not None:
                query = query.filter(Product.is_featured == filter_params.is_featured)
            
            if filter_params.status:
                query = query.filter(Product.status == filter_params.status)
            
            if filter_params.search:
                search_term = f"%{filter_params.search}%"
                query = query.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term),
                        Product.short_description.ilike(search_term)
                    )
                )
            
            # Apply sorting
            if filter_params.sort_by:
                if hasattr(Product, filter_params.sort_by):
                    sort_column = getattr(Product, filter_params.sort_by)
                    if filter_params.sort_order == "asc":
                        query = query.order_by(asc(sort_column))
                    else:
                        query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(desc(Product.created_at))
            else:
                query = query.order_by(desc(Product.created_at))
            
            # Apply pagination
            return query.offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting products by filter: {e}")
            raise
    
    def get_product_by_slug(self, slug: str) -> Optional[Product]:
        """Mendapatkan produk berdasarkan slug"""
        try:
            return self.db.query(Product).filter(Product.slug == slug).first()
        except Exception as e:
            logger.error(f"Error getting product by slug: {e}")
            raise
    
    def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Mendapatkan produk unggulan"""
        try:
            return self.db.query(Product).filter(
                and_(
                    Product.is_featured == True,
                    Product.status == "active"
                )
            ).order_by(desc(Product.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting featured products: {e}")
            raise
    
    def get_products_by_category(self, category: str, limit: int = 20) -> List[Product]:
        """Mendapatkan produk berdasarkan kategori"""
        try:
            return self.db.query(Product).filter(
                and_(
                    Product.category == category,
                    Product.status == "active"
                )
            ).order_by(desc(Product.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting products by category: {e}")
            raise
    
    def update_product_view_count(self, product_id: int) -> bool:
        """Update view count produk"""
        try:
            self.db.query(Product).filter(Product.id == product_id).update(
                {Product.view_count: Product.view_count + 1}
            )
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating product view count: {e}")
            self.db.rollback()
            return False
    
    def update_product_purchase_count(self, product_id: int) -> bool:
        """Update purchase count produk"""
        try:
            self.db.query(Product).filter(Product.id == product_id).update(
                {Product.purchase_count: Product.purchase_count + 1}
            )
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating product purchase count: {e}")
            self.db.rollback()
            return False
    
    def get_product_categories(self) -> List[Dict[str, Any]]:
        """Mendapatkan daftar kategori produk"""
        try:
            result = self.db.query(
                Product.category,
                func.count(Product.id).label('product_count')
            ).filter(
                Product.status == "active"
            ).group_by(Product.category).all()
            
            return [
                {
                    'category': row.category,
                    'product_count': row.product_count
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Error getting product categories: {e}")
            raise

class VoucherRepository(BaseRepository[Voucher]):
    """
    Repository untuk menangani operasi database voucher.
    """
    
    def __init__(self, db: Session):
        super().__init__(Voucher, db)
    
    def create_voucher(self, voucher_data: VoucherCreate) -> Voucher:
        """Membuat voucher baru"""
        try:
            # Convert lists to JSON strings
            applicable_products_json = json.dumps(voucher_data.applicable_products) if voucher_data.applicable_products else None
            applicable_categories_json = json.dumps(voucher_data.applicable_categories) if voucher_data.applicable_categories else None
            excluded_products_json = json.dumps(voucher_data.excluded_products) if voucher_data.excluded_products else None
            applicable_users_json = json.dumps(voucher_data.applicable_users) if voucher_data.applicable_users else None
            
            db_voucher = Voucher(
                code=voucher_data.code,
                name=voucher_data.name,
                description=voucher_data.description,
                voucher_type=voucher_data.voucher_type,
                discount_value=voucher_data.discount_value,
                max_discount_amount=voucher_data.max_discount_amount,
                minimum_order_amount=voucher_data.minimum_order_amount,
                maximum_order_amount=voucher_data.maximum_order_amount,
                usage_limit=voucher_data.usage_limit,
                usage_limit_per_user=voucher_data.usage_limit_per_user,
                valid_from=voucher_data.valid_from,
                valid_until=voucher_data.valid_until,
                applicable_products=applicable_products_json,
                applicable_categories=applicable_categories_json,
                excluded_products=excluded_products_json,
                applicable_users=applicable_users_json,
                new_users_only=voucher_data.new_users_only,
                is_public=voucher_data.is_public
            )
            
            self.db.add(db_voucher)
            self.db.commit()
            self.db.refresh(db_voucher)
            
            logger.info(f"Voucher created: {voucher_data.code}")
            return db_voucher
            
        except Exception as e:
            logger.error(f"Error creating voucher: {e}")
            self.db.rollback()
            raise
    
    def get_voucher_by_code(self, code: str) -> Optional[Voucher]:
        """Mendapatkan voucher berdasarkan kode"""
        try:
            return self.db.query(Voucher).filter(Voucher.code == code).first()
        except Exception as e:
            logger.error(f"Error getting voucher by code: {e}")
            raise
    
    def get_vouchers_by_filter(self, filter_params: VoucherFilter,
                              limit: int = 20, offset: int = 0) -> List[Voucher]:
        """Mendapatkan voucher berdasarkan filter"""
        try:
            query = self.db.query(Voucher)
            
            # Apply filters
            if filter_params.voucher_type:
                query = query.filter(Voucher.voucher_type == filter_params.voucher_type)
            
            if filter_params.status:
                query = query.filter(Voucher.status == filter_params.status)
            
            if filter_params.is_public is not None:
                query = query.filter(Voucher.is_public == filter_params.is_public)
            
            if filter_params.valid_now:
                now = datetime.utcnow()
                query = query.filter(
                    and_(
                        Voucher.valid_from <= now,
                        Voucher.valid_until >= now,
                        Voucher.status == "active"
                    )
                )
            
            if filter_params.search:
                search_term = f"%{filter_params.search}%"
                query = query.filter(
                    or_(
                        Voucher.code.ilike(search_term),
                        Voucher.name.ilike(search_term),
                        Voucher.description.ilike(search_term)
                    )
                )
            
            # Apply sorting
            if filter_params.sort_by:
                if hasattr(Voucher, filter_params.sort_by):
                    sort_column = getattr(Voucher, filter_params.sort_by)
                    if filter_params.sort_order == "asc":
                        query = query.order_by(asc(sort_column))
                    else:
                        query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(desc(Voucher.created_at))
            else:
                query = query.order_by(desc(Voucher.created_at))
            
            # Apply pagination
            return query.offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting vouchers by filter: {e}")
            raise
    
    def get_active_vouchers(self, limit: int = 20) -> List[Voucher]:
        """Mendapatkan voucher yang aktif"""
        try:
            now = datetime.utcnow()
            return self.db.query(Voucher).filter(
                and_(
                    Voucher.status == "active",
                    Voucher.valid_from <= now,
                    Voucher.valid_until >= now,
                    Voucher.is_public == True
                )
            ).order_by(desc(Voucher.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting active vouchers: {e}")
            raise
    
    def validate_voucher(self, code: str, user_id: int, order_amount: float,
                        product_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Validasi voucher"""
        try:
            voucher = self.get_voucher_by_code(code)
            
            if not voucher:
                return {
                    'is_valid': False,
                    'message': 'Voucher tidak ditemukan',
                    'discount_amount': 0
                }
            
            now = datetime.utcnow()
            
            # Check if voucher is active
            if voucher.status != "active":
                return {
                    'is_valid': False,
                    'message': 'Voucher tidak aktif',
                    'discount_amount': 0
                }
            
            # Check validity period
            if now < voucher.valid_from or now > voucher.valid_until:
                return {
                    'is_valid': False,
                    'message': 'Voucher sudah tidak berlaku',
                    'discount_amount': 0
                }
            
            # Check usage limit
            if voucher.usage_limit and voucher.current_usage_count >= voucher.usage_limit:
                return {
                    'is_valid': False,
                    'message': 'Voucher sudah mencapai batas penggunaan',
                    'discount_amount': 0
                }
            
            # Check user usage limit
            if voucher.usage_limit_per_user:
                user_usage_count = self.db.query(VoucherUsage).filter(
                    and_(
                        VoucherUsage.voucher_id == voucher.id,
                        VoucherUsage.user_id == user_id
                    )
                ).count()
                
                if user_usage_count >= voucher.usage_limit_per_user:
                    return {
                        'is_valid': False,
                        'message': 'Anda sudah mencapai batas penggunaan voucher ini',
                        'discount_amount': 0
                    }
            
            # Check minimum order amount
            if voucher.minimum_order_amount and order_amount < voucher.minimum_order_amount:
                return {
                    'is_valid': False,
                    'message': f'Minimal order Rp {voucher.minimum_order_amount:,.0f}',
                    'discount_amount': 0
                }
            
            # Check maximum order amount
            if voucher.maximum_order_amount and order_amount > voucher.maximum_order_amount:
                return {
                    'is_valid': False,
                    'message': f'Maksimal order Rp {voucher.maximum_order_amount:,.0f}',
                    'discount_amount': 0
                }
            
            # Calculate discount amount
            discount_amount = 0
            if voucher.voucher_type == "percentage":
                discount_amount = (order_amount * voucher.discount_value) / 100
                if voucher.max_discount_amount and discount_amount > voucher.max_discount_amount:
                    discount_amount = voucher.max_discount_amount
            elif voucher.voucher_type == "fixed_amount":
                discount_amount = min(voucher.discount_value, order_amount)
            
            return {
                'is_valid': True,
                'message': 'Voucher valid',
                'discount_amount': float(discount_amount),
                'voucher_id': voucher.id,
                'voucher_name': voucher.name
            }
            
        except Exception as e:
            logger.error(f"Error validating voucher: {e}")
            return {
                'is_valid': False,
                'message': 'Terjadi kesalahan saat validasi voucher',
                'discount_amount': 0
            }
    
    def record_voucher_usage(self, voucher_id: int, user_id: int, 
                           discount_amount: float, order_amount: float,
                           order_id: Optional[int] = None,
                           ip_address: Optional[str] = None,
                           user_agent: Optional[str] = None) -> VoucherUsage:
        """Mencatat penggunaan voucher"""
        try:
            # Create voucher usage record
            voucher_usage = VoucherUsage(
                voucher_id=voucher_id,
                user_id=user_id,
                order_id=order_id,
                discount_amount=discount_amount,
                order_amount=order_amount,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(voucher_usage)
            
            # Update voucher usage count and total discount
            self.db.query(Voucher).filter(Voucher.id == voucher_id).update({
                Voucher.current_usage_count: Voucher.current_usage_count + 1,
                Voucher.usage_count: Voucher.usage_count + 1,
                Voucher.total_discount_given: Voucher.total_discount_given + discount_amount
            })
            
            self.db.commit()
            self.db.refresh(voucher_usage)
            
            logger.info(f"Voucher usage recorded: voucher_id={voucher_id}, user_id={user_id}")
            return voucher_usage
            
        except Exception as e:
            logger.error(f"Error recording voucher usage: {e}")
            self.db.rollback()
            raise
