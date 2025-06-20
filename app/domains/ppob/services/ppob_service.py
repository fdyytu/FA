"""
PPOB Service - Modular Implementation
Service utama PPOB yang menggunakan composition pattern
"""

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.ppob.repositories.ppob_repository import PPOBRepository
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, PPOBCategory, TransactionStatus
from app.domains.ppob.schemas.ppob_schemas import (
    PPOBInquiryRequest, PPOBInquiryResponse, PPOBPaymentRequest,
    PPOBTransactionCreate, PPOBTransactionUpdate
)

# Import modular services
from .ppob_product_service import PPOBProductService
from .ppob_transaction_service import PPOBTransactionService
from .ppob_payment_service import PPOBPaymentService

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None


class PPOBService(BaseService):
    """
    Service utama untuk menangani transaksi PPOB.
    Menggunakan composition pattern untuk memisahkan tanggung jawab.
    """
    
    def __init__(self, repository: PPOBRepository):
        super().__init__(repository)
        
        # Initialize sub-services
        self.product_service = PPOBProductService(repository)
        self.transaction_service = PPOBTransactionService(repository)
        self.payment_service = PPOBPaymentService(repository)
    
    # Product operations - delegate to product service
    async def get_products_by_category(self, category: PPOBCategory) -> List[PPOBProduct]:
        """Ambil produk berdasarkan kategori"""
        return await self.product_service.get_products_by_category(category)
    
    async def get_product_by_code(self, product_code: str) -> Optional[PPOBProduct]:
        """Ambil produk berdasarkan kode"""
        return await self.product_service.get_product_by_code(product_code)
    
    async def get_all_categories(self) -> List[PPOBCategory]:
        """Ambil semua kategori produk"""
        return await self.product_service.get_all_categories()
    
    async def search_products(self, query: str, category_id: Optional[int] = None) -> List[PPOBProduct]:
        """Cari produk berdasarkan query"""
        return await self.product_service.search_products(query, category_id)
    
    async def get_popular_products(self, limit: int = 10) -> List[PPOBProduct]:
        """Ambil produk populer"""
        return await self.product_service.get_popular_products(limit)
    
    # Payment operations - delegate to payment service
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Lakukan inquiry ke provider"""
        return await self.payment_service.inquiry(request)
    
    async def process_payment(self, transaction_id: int) -> PPOBTransaction:
        """Proses pembayaran ke provider"""
        return await self.payment_service.process_payment(transaction_id)
    
    async def check_transaction_status(self, transaction_id: int) -> Dict[str, Any]:
        """Cek status transaksi dari provider"""
        return await self.payment_service.check_transaction_status(transaction_id)
    
    # Transaction operations - delegate to transaction service
    async def create_transaction(self, user: User, request: PPOBPaymentRequest) -> PPOBTransaction:
        """Buat transaksi baru"""
        # Convert payment request to transaction create
        transaction_data = PPOBTransactionCreate(
            product_code=request.product_code,
            customer_number=request.customer_number,
            amount=request.amount,
            notes=getattr(request, 'notes', None)
        )
        return await self.transaction_service.create_transaction(user, transaction_data)
    
    def get_user_transactions(
        self, 
        user_id: int, 
        status: Optional[TransactionStatus] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[PPOBTransaction]:
        """Ambil transaksi user"""
        return self.transaction_service.get_user_transactions(user_id, status, limit, offset)
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[PPOBTransaction]:
        """Ambil transaksi berdasarkan ID"""
        return self.transaction_service.get_transaction_by_id(transaction_id)
    
    def get_transaction_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik transaksi"""
        return self.transaction_service.get_transaction_stats(user_id)
    
    async def update_transaction_status(
        self, 
        transaction_id: int, 
        status: TransactionStatus,
        notes: Optional[str] = None
    ) -> PPOBTransaction:
        """Update status transaksi"""
        return await self.transaction_service.update_transaction_status(transaction_id, status, notes)
    
    async def cancel_transaction(self, transaction_id: int, reason: str) -> PPOBTransaction:
        """Batalkan transaksi"""
        return await self.transaction_service.cancel_transaction(transaction_id, reason)
    
    async def get_transaction_history(
        self, 
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50
    ) -> List[PPOBTransaction]:
        """Ambil riwayat transaksi dengan filter tanggal"""
        return await self.transaction_service.get_transaction_history(user_id, start_date, end_date, limit)
