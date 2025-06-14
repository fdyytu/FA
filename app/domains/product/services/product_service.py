from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.domains.product.repositories.product_repository import ProductRepository, VoucherRepository
from app.domains.product.schemas.product_schemas import (
    ProductCreate, ProductUpdate, ProductFilter,
    VoucherCreate, VoucherUpdate, VoucherFilter,
    VoucherValidationRequest, VoucherValidationResponse
)
from app.domains.product.models.product import Product, Voucher, VoucherUsage
from app.shared.base_classes.base_service import BaseService
from app.domains.analytics.services.analytics_service import AnalyticsService
import logging
import json
from decimal import Decimal

logger = logging.getLogger(__name__)

class ProductService(BaseService):
    """
    Service untuk menangani business logic produk.
    Mengimplementasikan Single Responsibility Principle.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository(db)
        self.analytics_service = AnalyticsService(db)
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Membuat produk baru"""
        try:
            # Validate slug uniqueness
            existing_product = self.repository.get_product_by_slug(product_data.slug)
            if existing_product:
                raise ValueError("Slug sudah digunakan")
            
            # Create product
            product = self.repository.create_product(product_data)
            
            # Track analytics event
            await self.analytics_service.track_event({
                "event_type": "product_created",
                "product_id": product.id,
                "event_data": {"product_name": product.name, "category": product.category}
            })
            
            return product
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise
    
    async def get_product_by_id(self, product_id: int, track_view: bool = True) -> Optional[Product]:
        """Mendapatkan produk berdasarkan ID"""
        try:
            product = self.repository.get_by_id(product_id)
            
            if product and track_view:
                # Update view count
                self.repository.update_product_view_count(product_id)
                
                # Track analytics
                await self.analytics_service.track_product_view(product_id)
            
            return product
            
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            raise
    
    async def get_product_by_slug(self, slug: str, track_view: bool = True) -> Optional[Product]:
        """Mendapatkan produk berdasarkan slug"""
        try:
            product = self.repository.get_product_by_slug(slug)
            
            if product and track_view:
                # Update view count
                self.repository.update_product_view_count(product.id)
                
                # Track analytics
                await self.analytics_service.track_product_view(product.id)
            
            return product
            
        except Exception as e:
            logger.error(f"Error getting product by slug: {e}")
            raise
    
    async def get_products(self, filter_params: ProductFilter, 
                          limit: int = 20, offset: int = 0) -> List[Product]:
        """Mendapatkan daftar produk berdasarkan filter"""
        try:
            return self.repository.get_products_by_filter(filter_params, limit, offset)
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise
    
    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update produk"""
        try:
            product = self.repository.get_by_id(product_id)
            if not product:
                return None
            
            # Prepare update data
            update_data = {}
            for field, value in product_data.dict(exclude_unset=True).items():
                if field in ['tags', 'gallery_images'] and value is not None:
                    update_data[field] = json.dumps(value)
                else:
                    update_data[field] = value
            
            # Update product
            updated_product = self.repository.update(product_id, update_data)
            
            return updated_product
            
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            raise
    
    async def delete_product(self, product_id: int) -> bool:
        """Hapus produk (soft delete)"""
        try:
            return self.repository.delete(product_id)
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            raise
    
    async def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Mendapatkan produk unggulan"""
        try:
            return self.repository.get_featured_products(limit)
        except Exception as e:
            logger.error(f"Error getting featured products: {e}")
            raise
    
    async def get_products_by_category(self, category: str, limit: int = 20) -> List[Product]:
        """Mendapatkan produk berdasarkan kategori"""
        try:
            return self.repository.get_products_by_category(category, limit)
        except Exception as e:
            logger.error(f"Error getting products by category: {e}")
            raise
    
    async def get_product_categories(self) -> List[Dict[str, Any]]:
        """Mendapatkan daftar kategori produk"""
        try:
            return self.repository.get_product_categories()
        except Exception as e:
            logger.error(f"Error getting product categories: {e}")
            raise
    
    async def search_products(self, query: str, limit: int = 20) -> List[Product]:
        """Pencarian produk"""
        try:
            filter_params = ProductFilter(
                search=query,
                status="active",
                sort_by="view_count",
                sort_order="desc"
            )
            return self.repository.get_products_by_filter(filter_params, limit, 0)
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise

class VoucherService(BaseService):
    """
    Service untuk menangani business logic voucher.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = VoucherRepository(db)
        self.analytics_service = AnalyticsService(db)
    
    async def create_voucher(self, voucher_data: VoucherCreate) -> Voucher:
        """Membuat voucher baru"""
        try:
            # Validate code uniqueness
            existing_voucher = self.repository.get_voucher_by_code(voucher_data.code)
            if existing_voucher:
                raise ValueError("Kode voucher sudah digunakan")
            
            # Create voucher
            voucher = self.repository.create_voucher(voucher_data)
            
            # Track analytics event
            await self.analytics_service.track_event({
                "event_type": "voucher_created",
                "voucher_id": voucher.id,
                "event_data": {
                    "voucher_code": voucher.code,
                    "voucher_type": voucher.voucher_type,
                    "discount_value": float(voucher.discount_value)
                }
            })
            
            return voucher
            
        except Exception as e:
            logger.error(f"Error creating voucher: {e}")
            raise
    
    async def get_voucher_by_id(self, voucher_id: int) -> Optional[Voucher]:
        """Mendapatkan voucher berdasarkan ID"""
        try:
            return self.repository.get_by_id(voucher_id)
        except Exception as e:
            logger.error(f"Error getting voucher by ID: {e}")
            raise
    
    async def get_voucher_by_code(self, code: str) -> Optional[Voucher]:
        """Mendapatkan voucher berdasarkan kode"""
        try:
            return self.repository.get_voucher_by_code(code)
        except Exception as e:
            logger.error(f"Error getting voucher by code: {e}")
            raise
    
    async def get_vouchers(self, filter_params: VoucherFilter,
                          limit: int = 20, offset: int = 0) -> List[Voucher]:
        """Mendapatkan daftar voucher berdasarkan filter"""
        try:
            return self.repository.get_vouchers_by_filter(filter_params, limit, offset)
        except Exception as e:
            logger.error(f"Error getting vouchers: {e}")
            raise
    
    async def get_active_vouchers(self, limit: int = 20) -> List[Voucher]:
        """Mendapatkan voucher yang aktif"""
        try:
            return self.repository.get_active_vouchers(limit)
        except Exception as e:
            logger.error(f"Error getting active vouchers: {e}")
            raise
    
    async def update_voucher(self, voucher_id: int, voucher_data: VoucherUpdate) -> Optional[Voucher]:
        """Update voucher"""
        try:
            voucher = self.repository.get_by_id(voucher_id)
            if not voucher:
                return None
            
            # Prepare update data
            update_data = {}
            for field, value in voucher_data.dict(exclude_unset=True).items():
                if field in ['applicable_products', 'applicable_categories', 
                           'excluded_products', 'applicable_users'] and value is not None:
                    update_data[field] = json.dumps(value)
                else:
                    update_data[field] = value
            
            # Update voucher
            updated_voucher = self.repository.update(voucher_id, update_data)
            
            return updated_voucher
            
        except Exception as e:
            logger.error(f"Error updating voucher: {e}")
            raise
    
    async def delete_voucher(self, voucher_id: int) -> bool:
        """Hapus voucher (soft delete)"""
        try:
            return self.repository.delete(voucher_id)
        except Exception as e:
            logger.error(f"Error deleting voucher: {e}")
            raise
    
    async def validate_voucher(self, validation_request: VoucherValidationRequest) -> VoucherValidationResponse:
        """Validasi voucher"""
        try:
            result = self.repository.validate_voucher(
                code=validation_request.code,
                user_id=validation_request.user_id,
                order_amount=float(validation_request.order_amount),
                product_ids=validation_request.product_ids
            )
            
            return VoucherValidationResponse(
                is_valid=result['is_valid'],
                discount_amount=Decimal(str(result['discount_amount'])),
                message=result['message'],
                voucher_id=result.get('voucher_id'),
                voucher_name=result.get('voucher_name')
            )
            
        except Exception as e:
            logger.error(f"Error validating voucher: {e}")
            return VoucherValidationResponse(
                is_valid=False,
                discount_amount=Decimal('0'),
                message="Terjadi kesalahan saat validasi voucher"
            )
    
    async def use_voucher(self, voucher_id: int, user_id: int, 
                         discount_amount: Decimal, order_amount: Decimal,
                         order_id: Optional[int] = None,
                         ip_address: Optional[str] = None,
                         user_agent: Optional[str] = None) -> VoucherUsage:
        """Menggunakan voucher"""
        try:
            # Record voucher usage
            voucher_usage = self.repository.record_voucher_usage(
                voucher_id=voucher_id,
                user_id=user_id,
                discount_amount=float(discount_amount),
                order_amount=float(order_amount),
                order_id=order_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Track analytics
            await self.analytics_service.track_voucher_usage(
                voucher_id=voucher_id,
                user_id=user_id,
                discount_amount=discount_amount,
                transaction_id=order_id
            )
            
            return voucher_usage
            
        except Exception as e:
            logger.error(f"Error using voucher: {e}")
            raise
    
    async def get_user_voucher_usage(self, user_id: int, limit: int = 20) -> List[VoucherUsage]:
        """Mendapatkan riwayat penggunaan voucher user"""
        try:
            from app.domains.product.models.product import VoucherUsage
            return self.db.query(VoucherUsage).filter(
                VoucherUsage.user_id == user_id
            ).order_by(VoucherUsage.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting user voucher usage: {e}")
            raise
    
    async def get_voucher_statistics(self, voucher_id: int) -> Dict[str, Any]:
        """Mendapatkan statistik voucher"""
        try:
            voucher = self.repository.get_by_id(voucher_id)
            if not voucher:
                return {}
            
            from app.domains.product.models.product import VoucherUsage
            
            # Get usage statistics
            usage_stats = self.db.query(
                func.count(VoucherUsage.id).label('total_usage'),
                func.sum(VoucherUsage.discount_amount).label('total_discount'),
                func.avg(VoucherUsage.order_amount).label('avg_order_amount'),
                func.count(func.distinct(VoucherUsage.user_id)).label('unique_users')
            ).filter(VoucherUsage.voucher_id == voucher_id).first()
            
            return {
                'voucher_id': voucher_id,
                'voucher_code': voucher.code,
                'voucher_name': voucher.name,
                'total_usage': usage_stats.total_usage or 0,
                'total_discount_given': float(usage_stats.total_discount or 0),
                'average_order_amount': float(usage_stats.avg_order_amount or 0),
                'unique_users': usage_stats.unique_users or 0,
                'usage_limit': voucher.usage_limit,
                'remaining_usage': (voucher.usage_limit - voucher.current_usage_count) if voucher.usage_limit else None,
                'conversion_rate': (usage_stats.total_usage / voucher.view_count * 100) if hasattr(voucher, 'view_count') and voucher.view_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting voucher statistics: {e}")
            raise
