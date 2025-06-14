from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.shared.base_classes.base import BaseModel
from datetime import datetime
import enum

class ProductStatus(enum.Enum):
    """Status produk"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"

class VoucherType(enum.Enum):
    """Tipe voucher"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_SHIPPING = "free_shipping"
    BUY_ONE_GET_ONE = "bogo"

class VoucherStatus(enum.Enum):
    """Status voucher"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    USED_UP = "used_up"

class Product(BaseModel):
    """
    Model untuk produk.
    Mengimplementasikan Single Responsibility Principle - hanya menangani data produk.
    """
    __tablename__ = "products"
    
    # Basic product info
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(250), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Product categorization
    category = Column(String(50), nullable=False, index=True)
    subcategory = Column(String(50), nullable=True, index=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False)
    cost_price = Column(Numeric(15, 2), nullable=True)  # For profit calculation
    compare_at_price = Column(Numeric(15, 2), nullable=True)  # Original price for discounts
    
    # Inventory
    sku = Column(String(100), unique=True, index=True, nullable=True)
    stock_quantity = Column(Integer, default=0)
    track_inventory = Column(Boolean, default=True)
    allow_backorder = Column(Boolean, default=False)
    
    # Product attributes
    weight = Column(Numeric(10, 3), nullable=True)  # in kg
    dimensions = Column(String(100), nullable=True)  # "L x W x H"
    
    # SEO and marketing
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)
    featured_image = Column(String(500), nullable=True)
    gallery_images = Column(Text, nullable=True)  # JSON array of image URLs
    
    # Status and visibility
    status = Column(String(20), default=ProductStatus.DRAFT.value, index=True)
    is_featured = Column(Boolean, default=False, index=True)
    is_digital = Column(Boolean, default=False)
    requires_shipping = Column(Boolean, default=True)
    
    # Analytics fields
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    rating_average = Column(Numeric(3, 2), default=0)
    rating_count = Column(Integer, default=0)
    
    # Timestamps
    published_at = Column(DateTime, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_category_status', 'category', 'status'),
        Index('idx_product_featured_status', 'is_featured', 'status'),
        Index('idx_product_price_range', 'price', 'status'),
    )

class Voucher(BaseModel):
    """
    Model untuk voucher/kupon diskon.
    """
    __tablename__ = "vouchers"
    
    # Basic voucher info
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Voucher type and value
    voucher_type = Column(String(20), nullable=False, index=True)  # percentage, fixed_amount, etc.
    discount_value = Column(Numeric(15, 2), nullable=False)  # percentage or amount
    max_discount_amount = Column(Numeric(15, 2), nullable=True)  # for percentage discounts
    
    # Usage conditions
    minimum_order_amount = Column(Numeric(15, 2), nullable=True)
    maximum_order_amount = Column(Numeric(15, 2), nullable=True)
    
    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # total usage limit
    usage_limit_per_user = Column(Integer, nullable=True)
    current_usage_count = Column(Integer, default=0)
    
    # Validity period
    valid_from = Column(DateTime, nullable=False, index=True)
    valid_until = Column(DateTime, nullable=False, index=True)
    
    # Applicable products/categories
    applicable_products = Column(Text, nullable=True)  # JSON array of product IDs
    applicable_categories = Column(Text, nullable=True)  # JSON array of categories
    excluded_products = Column(Text, nullable=True)  # JSON array of excluded product IDs
    
    # User restrictions
    applicable_users = Column(Text, nullable=True)  # JSON array of user IDs (if specific users)
    new_users_only = Column(Boolean, default=False)
    
    # Status
    status = Column(String(20), default=VoucherStatus.ACTIVE.value, index=True)
    is_public = Column(Boolean, default=True)  # public or private voucher
    
    # Analytics
    usage_count = Column(Integer, default=0)
    total_discount_given = Column(Numeric(15, 2), default=0)
    
    # Indexes
    __table_args__ = (
        Index('idx_voucher_validity', 'valid_from', 'valid_until'),
        Index('idx_voucher_status_public', 'status', 'is_public'),
        Index('idx_voucher_type_status', 'voucher_type', 'status'),
    )

class VoucherUsage(BaseModel):
    """
    Model untuk tracking penggunaan voucher.
    """
    __tablename__ = "voucher_usages"
    
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_id = Column(Integer, nullable=True, index=True)  # if integrated with orders
    
    # Usage details
    discount_amount = Column(Numeric(15, 2), nullable=False)
    order_amount = Column(Numeric(15, 2), nullable=False)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Unique constraint to prevent duplicate usage
    __table_args__ = (
        Index('idx_voucher_usage_unique', 'voucher_id', 'user_id', 'order_id', unique=True),
        Index('idx_voucher_usage_user_date', 'user_id', 'created_at'),
    )
