"""
Margin Calculation Service - Kalkulasi margin
Dipecah dari margin_management_service.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.admin.repositories.admin_repository import PPOBMarginRepository


class MarginCalculationService(BaseService):
    """Service untuk kalkulasi margin"""
    
    def __init__(self, db: Session):
        self.db = db
        self.margin_repo = PPOBMarginRepository(db)
    
    def calculate_price_with_margin(
        self, 
        base_price: Decimal, 
        category: str, 
        product_code: Optional[str] = None
    ) -> Decimal:
        """Hitung harga dengan margin - KISS principle: Simple calculation"""
        # Try to get product-specific margin first
        margin_config = None
        if product_code:
            margin_config = self.margin_repo.get_by_product_code(product_code)
        
        # If no product-specific margin, get category margin
        if not margin_config:
            margin_config = self.margin_repo.get_global_margin(category)
        
        # If no margin config found, return base price
        if not margin_config:
            return base_price
        
        # Calculate margin
        if margin_config.margin_type == "percentage":
            margin_amount = base_price * (margin_config.margin_value / 100)
        else:  # fixed
            margin_amount = margin_config.margin_value
        
        return base_price + margin_amount
    
    def calculate_margin_amount(
        self,
        base_price: Decimal,
        margin_type: str,
        margin_value: Decimal
    ) -> Decimal:
        """Hitung jumlah margin berdasarkan tipe dan nilai"""
        if margin_type == "percentage":
            return base_price * (margin_value / 100)
        else:  # fixed
            return margin_value
    
    def calculate_profit_percentage(
        self,
        base_price: Decimal,
        selling_price: Decimal
    ) -> Decimal:
        """Hitung persentase profit"""
        if base_price <= 0:
            return Decimal('0')
        
        profit = selling_price - base_price
        return (profit / base_price) * 100
    
    def calculate_bulk_prices(
        self,
        products: list,
        category: str
    ) -> list:
        """Hitung harga dengan margin untuk multiple produk"""
        results = []
        
        for product in products:
            base_price = Decimal(str(product.get('base_price', 0)))
            product_code = product.get('product_code')
            
            final_price = self.calculate_price_with_margin(
                base_price, category, product_code
            )
            
            results.append({
                'product_code': product_code,
                'base_price': base_price,
                'final_price': final_price,
                'margin_amount': final_price - base_price
            })
        
        return results
    
    def get_margin_config_for_product(
        self,
        category: str,
        product_code: Optional[str] = None
    ):
        """Ambil konfigurasi margin untuk produk"""
        # Try product-specific first
        if product_code:
            config = self.margin_repo.get_by_product_code(product_code)
            if config:
                return config
        
        # Fallback to category margin
        return self.margin_repo.get_global_margin(category)
    
    def preview_price_changes(
        self,
        new_margin_type: str,
        new_margin_value: Decimal,
        category: str,
        sample_prices: list
    ) -> list:
        """Preview perubahan harga dengan margin baru"""
        previews = []
        
        for price in sample_prices:
            base_price = Decimal(str(price))
            
            # Calculate with new margin
            if new_margin_type == "percentage":
                margin_amount = base_price * (new_margin_value / 100)
            else:
                margin_amount = new_margin_value
            
            new_price = base_price + margin_amount
            
            previews.append({
                'base_price': base_price,
                'margin_amount': margin_amount,
                'final_price': new_price,
                'profit_percentage': self.calculate_profit_percentage(base_price, new_price)
            })
        
        return previews
