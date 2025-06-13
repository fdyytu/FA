from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from decimal import Decimal

from app.shared.base_classes.base_service import BaseService
from app.domains.ppob.repositories.ppob_repository import PPOBRepository
from app.domains.ppob.models.ppob import PPOBTransaction, PPOBProduct, PPOBCategory, TransactionStatus
from app.domains.ppob.schemas.ppob_schemas import (
    PPOBInquiryRequest, PPOBInquiryResponse, PPOBPaymentRequest,
    PPOBTransactionCreate, PPOBTransactionUpdate
)

# Try to import User from domains
try:
    from app.domains.auth.models.user import User
except ImportError:
    User = None

try:
    from app.services.ppob.providers import DefaultPPOBProvider
    from app.services.ppob.providers.digiflazz_provider import DigiflazzProvider
except ImportError:
    DefaultPPOBProvider = DigiflazzProvider = None

try:
    from app.services.admin_service import AdminConfigService, PPOBMarginService
except ImportError:
    AdminConfigService = PPOBMarginService = None

from app.core.config import settings

try:
    from app.cache.managers.ppob_cache_manager import ppob_cache_manager
except ImportError:
    ppob_cache_manager = None

class PPOBService(BaseService):
    """
    Service untuk menangani transaksi PPOB.
    Mengimplementasikan Single Responsibility Principle - hanya menangani logika bisnis PPOB.
    """
    
    def __init__(self, repository: PPOBRepository):
        super().__init__(repository)
        self.admin_service = AdminConfigService(repository.db)
        self.margin_service = PPOBMarginService(repository.db)
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Ambil provider berdasarkan konfigurasi admin (Factory Pattern)"""
        try:
            # Coba ambil konfigurasi Digiflazz
            digiflazz_config = self.admin_service.get_digiflazz_config()
            
            if digiflazz_config["is_configured"]:
                return DigiflazzProvider(
                    username=digiflazz_config["username"],
                    api_key=digiflazz_config["api_key"],
                    production=digiflazz_config["production"]
                )
            else:
                # Fallback ke default provider
                return DefaultPPOBProvider(
                    api_url=settings.PPOB_API_URL,
                    api_key=settings.PPOB_API_KEY,
                    timeout=settings.PPOB_TIMEOUT
                )
        except Exception as e:
            # Jika ada error, gunakan default provider
            return DefaultPPOBProvider(
                api_url=settings.PPOB_API_URL,
                api_key=settings.PPOB_API_KEY,
                timeout=settings.PPOB_TIMEOUT
            )
    
    async def get_products_by_category(self, category: PPOBCategory) -> List[PPOBProduct]:
        """Ambil produk berdasarkan kategori dengan cache"""
        
        def fetch_from_db(cat: PPOBCategory) -> List[PPOBProduct]:
            """Function untuk fetch dari database"""
            return self.repository.get_products_by_category(cat)
        
        # Gunakan cache manager untuk get products
        return await ppob_cache_manager.get_products_by_category(
            category=category,
            fetch_func=fetch_from_db
        )
    
    async def get_product_by_code(self, product_code: str) -> Optional[PPOBProduct]:
        """Ambil produk berdasarkan kode dengan cache"""
        
        def fetch_from_db(code: str) -> Optional[PPOBProduct]:
            """Function untuk fetch dari database"""
            return self.repository.get_product_by_code(code)
        
        # Gunakan cache manager untuk get product
        return await ppob_cache_manager.get_product_by_code(
            product_code=product_code,
            fetch_func=fetch_from_db
        )
    
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Melakukan inquiry tagihan dengan cache"""
        try:
            # Validasi kategori didukung
            if request.category not in self.provider.get_supported_categories():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kategori {request.category.value} tidak didukung"
                )
            
            # Cek cache inquiry dulu
            cached_inquiry = await ppob_cache_manager.get_cached_inquiry(
                category=request.category,
                customer_number=request.customer_number
            )
            
            if cached_inquiry:
                # Return dari cache jika ada
                return PPOBInquiryResponse(**cached_inquiry)
            
            # Panggil provider untuk inquiry
            inquiry_result = await self.provider.inquiry(request)
            
            # Cache hasil inquiry
            await ppob_cache_manager.cache_inquiry_result(
                category=request.category,
                customer_number=request.customer_number,
                result=inquiry_result.dict()
            )
            
            return inquiry_result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal melakukan inquiry: {str(e)}"
            )
    
    async def create_transaction(self, user: User, request: PPOBPaymentRequest) -> PPOBTransaction:
        """Buat transaksi pembayaran PPOB"""
        try:
            # Validasi produk
            product = await self.get_product_by_code(request.product_code)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Produk tidak ditemukan"
                )
            
            # Generate transaction code
            transaction_code = self.provider._generate_transaction_code()
            
            # Hitung harga dengan margin
            base_price = product.price
            final_price = self.margin_service.calculate_price_with_margin(
                base_price=base_price,
                category=request.category.value,
                product_code=request.product_code
            )
            
            # Buat data transaksi
            transaction_data = PPOBTransactionCreate(
                category=request.category,
                product_code=request.product_code,
                customer_number=request.customer_number
            )
            
            # Buat transaksi menggunakan repository
            transaction = PPOBTransaction(
                user_id=user.id,
                transaction_code=transaction_code,
                category=request.category,
                product_code=request.product_code,
                product_name=product.product_name,
                customer_number=request.customer_number,
                amount=final_price,  # Gunakan harga dengan margin
                admin_fee=product.admin_fee,
                total_amount=final_price + product.admin_fee,
                status=TransactionStatus.PENDING
            )
            
            return self.repository.create(transaction)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat transaksi: {str(e)}"
            )
    
    async def process_payment(self, transaction_id: int) -> PPOBTransaction:
        """Proses pembayaran transaksi"""
        try:
            # Ambil transaksi
            transaction = self.repository.get_by_id(transaction_id)
            
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaksi tidak ditemukan"
                )
            
            if transaction.status != TransactionStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transaksi sudah diproses"
                )
            
            # Panggil provider untuk pembayaran
            payment_data = {
                "transaction_code": transaction.transaction_code,
                "product_code": transaction.product_code,
                "customer_number": transaction.customer_number,
                "amount": float(transaction.amount)
            }
            
            payment_result = await self.provider.payment(payment_data)
            
            # Update status transaksi
            update_data = PPOBTransactionUpdate()
            if payment_result.get("status") == "success":
                update_data.status = TransactionStatus.SUCCESS
                update_data.provider_ref = payment_result.get("transaction_id")
                update_data.notes = payment_result.get("message")
            else:
                update_data.status = TransactionStatus.FAILED
                update_data.notes = payment_result.get("message", "Pembayaran gagal")
            
            return self.repository.update(transaction_id, update_data.dict(exclude_unset=True))
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses pembayaran: {str(e)}"
            )
    
    def get_user_transactions(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[TransactionStatus] = None,
        category: Optional[PPOBCategory] = None
    ) -> List[PPOBTransaction]:
        """Ambil riwayat transaksi user"""
        return self.repository.get_user_transactions(
            user_id=user_id,
            skip=skip,
            limit=limit,
            status=status,
            category=category
        )
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[PPOBTransaction]:
        """Ambil transaksi berdasarkan ID"""
        return self.repository.get_by_id(transaction_id)
    
    def get_transaction_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Ambil statistik transaksi"""
        return self.repository.get_transaction_stats(user_id)
    
    def get_popular_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Ambil produk yang paling sering digunakan"""
        return self.repository.get_popular_products(limit)
    
    def get_monthly_revenue(self, year: int, month: int) -> Dict[str, Any]:
        """Ambil revenue bulanan"""
        return self.repository.get_monthly_revenue(year, month)
    
    async def cancel_transaction(self, transaction_id: int, user_id: int) -> PPOBTransaction:
        """Batalkan transaksi"""
        try:
            transaction = self.repository.get_by_id(transaction_id)
            
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaksi tidak ditemukan"
                )
            
            if transaction.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tidak memiliki akses ke transaksi ini"
                )
            
            if transaction.status != TransactionStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hanya transaksi pending yang bisa dibatalkan"
                )
            
            # Update status ke cancelled
            update_data = PPOBTransactionUpdate(
                status=TransactionStatus.CANCELLED,
                notes="Transaksi dibatalkan oleh user"
            )
            
            return self.repository.update(transaction_id, update_data.dict(exclude_unset=True))
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membatalkan transaksi: {str(e)}"
            )
    
    async def retry_failed_transaction(self, transaction_id: int) -> PPOBTransaction:
        """Retry transaksi yang gagal"""
        try:
            transaction = self.repository.get_by_id(transaction_id)
            
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaksi tidak ditemukan"
                )
            
            if transaction.status != TransactionStatus.FAILED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hanya transaksi gagal yang bisa di-retry"
                )
            
            # Reset status ke pending
            update_data = PPOBTransactionUpdate(
                status=TransactionStatus.PENDING,
                notes="Transaksi di-retry"
            )
            
            updated_transaction = self.repository.update(transaction_id, update_data.dict(exclude_unset=True))
            
            # Proses ulang pembayaran
            return await self.process_payment(transaction_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal retry transaksi: {str(e)}"
            )
