from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime
import json
from app.common.base_classes.base_service import BaseService
from app.domains.voucher.repositories.voucher_repository import VoucherRepository
from app.domains.voucher.models.voucher import Voucher, VoucherUsage, VoucherType, VoucherStatus
from app.domains.voucher.schemas.voucher_schemas import (
    VoucherCreate, VoucherUpdate, VoucherValidationRequest, VoucherValidationResponse
)

class VoucherService(BaseService):
    """
    Service untuk menangani voucher/promo.
    Mengimplementasikan Single Responsibility Principle - hanya logika bisnis voucher.
    """
    
    def __init__(self, repository: VoucherRepository):
        super().__init__(repository)
    
    async def create_voucher(self, voucher_data: VoucherCreate) -> Voucher:
        """Buat voucher baru"""
        # Validasi kode voucher unik
        existing = self.repository.get_by_code(voucher_data.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kode voucher sudah digunakan"
            )
        
        voucher_dict = voucher_data.dict()
        
        # Convert lists to JSON strings
        if voucher_dict.get('applicable_categories'):
            voucher_dict['applicable_categories'] = json.dumps(voucher_dict['applicable_categories'])
        if voucher_dict.get('applicable_products'):
            voucher_dict['applicable_products'] = json.dumps(voucher_dict['applicable_products'])
        
        return self.repository.create(voucher_dict)
    
    async def validate_voucher(
        self, 
        request: VoucherValidationRequest, 
        user_id: int
    ) -> VoucherValidationResponse:
        """Validasi voucher untuk transaksi"""
        voucher = self.repository.get_by_code(request.code)
        
        if not voucher:
            return VoucherValidationResponse(
                valid=False,
                final_amount=request.transaction_amount,
                message="Kode voucher tidak ditemukan"
            )
        
        # Check voucher status
        if voucher.status != VoucherStatus.ACTIVE:
            return VoucherValidationResponse(
                valid=False,
                final_amount=request.transaction_amount,
                message="Voucher tidak aktif"
            )
        
        # Check validity period
        now = datetime.now()
        if now < voucher.valid_from or now > voucher.valid_until:
            return VoucherValidationResponse(
                valid=False,
                final_amount=request.transaction_amount,
                message="Voucher sudah kadaluarsa atau belum berlaku"
            )
        
        # Check minimum transaction
        if request.transaction_amount < voucher.min_transaction:
            return VoucherValidationResponse(
                valid=False,
                final_amount=request.transaction_amount,
                message=f"Minimum transaksi Rp {voucher.min_transaction:,.0f}"
            )
        
        # Check usage limit
        if voucher.usage_limit and voucher.usage_count >= voucher.usage_limit:
            return VoucherValidationResponse(
                valid=False,
                final_amount=request.transaction_amount,
                message="Voucher sudah mencapai batas penggunaan"
            )
        
        # Check user usage limit
        user_usage_count = self.repository.get_user_usage_count(voucher.id, user_id)
        if user_usage_count >= voucher.user_limit:
            return VoucherValidationResponse(
                valid=False,
                final_amount=request.transaction_amount,
                message="Anda sudah mencapai batas penggunaan voucher ini"
            )
        
        # Check applicable categories
        if voucher.applicable_categories and request.category:
            categories = json.loads(voucher.applicable_categories)
            if request.category not in categories:
                return VoucherValidationResponse(
                    valid=False,
                    final_amount=request.transaction_amount,
                    message="Voucher tidak berlaku untuk kategori ini"
                )
        
        # Check applicable products
        if voucher.applicable_products and request.product_code:
            products = json.loads(voucher.applicable_products)
            if request.product_code not in products:
                return VoucherValidationResponse(
                    valid=False,
                    final_amount=request.transaction_amount,
                    message="Voucher tidak berlaku untuk produk ini"
                )
        
        # Calculate discount
        discount_amount = self._calculate_discount(voucher, request.transaction_amount)
        final_amount = request.transaction_amount - discount_amount
        
        return VoucherValidationResponse(
            valid=True,
            voucher_id=voucher.id,
            discount_amount=discount_amount,
            final_amount=final_amount,
            message="Voucher valid"
        )
    
    def _calculate_discount(self, voucher: Voucher, amount: Decimal) -> Decimal:
        """Hitung jumlah diskon"""
        if voucher.voucher_type == VoucherType.PERCENTAGE:
            discount = amount * (voucher.discount_value / 100)
            if voucher.max_discount:
                discount = min(discount, voucher.max_discount)
        elif voucher.voucher_type == VoucherType.FIXED_AMOUNT:
            discount = voucher.discount_value
        else:  # FREE_ADMIN_FEE
            # Assume admin fee is part of the amount or calculate separately
            discount = min(voucher.discount_value, amount)
        
        return min(discount, amount)  # Discount cannot exceed transaction amount
    
    async def use_voucher(
        self, 
        voucher_id: int, 
        user_id: int, 
        transaction_id: int,
        original_amount: Decimal,
        discount_amount: Decimal
    ) -> VoucherUsage:
        """Gunakan voucher untuk transaksi"""
        # Create voucher usage record
        usage_data = {
            "voucher_id": voucher_id,
            "user_id": user_id,
            "transaction_id": transaction_id,
            "discount_amount": discount_amount,
            "original_amount": original_amount,
            "final_amount": original_amount - discount_amount
        }
        
        usage = self.repository.create_usage(usage_data)
        
        # Update voucher usage count
        voucher = self.repository.get_by_id(voucher_id)
        self.repository.update(voucher_id, {"usage_count": voucher.usage_count + 1})
        
        return usage
    
    async def get_user_vouchers(self, user_id: int) -> List[Voucher]:
        """Ambil voucher yang bisa digunakan user"""
        return self.repository.get_available_vouchers(user_id)
    
    async def get_voucher_stats(self) -> dict:
        """Ambil statistik voucher"""
        return self.repository.get_voucher_stats()
