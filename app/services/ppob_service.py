from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from app.models.ppob import PPOBTransaction, PPOBProduct, TransactionStatus, PPOBCategory
from app.models.user import User
from app.schemas.ppob import (
    PPOBInquiryRequest, PPOBInquiryResponse, PPOBPaymentRequest,
    PPOBTransactionResponse, PPOBProductResponse
)
from app.services.ppob.providers import DefaultPPOBProvider
from app.services.ppob.providers.digiflazz_provider import DigiflazzProvider
from app.services.admin_service import AdminConfigService, PPOBMarginService
from app.core.config import settings

class PPOBService:
    """Service untuk menangani transaksi PPOB (Single Responsibility Principle)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.admin_service = AdminConfigService(db)
        self.margin_service = PPOBMarginService(db)
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Ambil provider berdasarkan konfigurasi admin"""
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
    
    def get_products_by_category(self, category: PPOBCategory) -> List[PPOBProduct]:
        """Ambil produk berdasarkan kategori"""
        return self.db.query(PPOBProduct).filter(
            PPOBProduct.category == category,
            PPOBProduct.is_active == "1"
        ).all()
    
    def get_product_by_code(self, product_code: str) -> Optional[PPOBProduct]:
        """Ambil produk berdasarkan kode"""
        return self.db.query(PPOBProduct).filter(
            PPOBProduct.product_code == product_code,
            PPOBProduct.is_active == "1"
        ).first()
    
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Melakukan inquiry tagihan"""
        try:
            # Validasi kategori didukung
            if request.category not in self.provider.get_supported_categories():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Kategori {request.category.value} tidak didukung"
                )
            
            # Panggil provider untuk inquiry
            inquiry_result = await self.provider.inquiry(request)
            return inquiry_result
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal melakukan inquiry: {str(e)}"
            )
    
    async def create_transaction(
        self, 
        user: User, 
        request: PPOBPaymentRequest
    ) -> PPOBTransaction:
        """Buat transaksi PPOB baru"""
        try:
            # Ambil produk
            product = self.get_product_by_code(request.product_code)
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
            
            # Buat transaksi
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
            
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            return transaction
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal membuat transaksi: {str(e)}"
            )
    
    async def process_payment(self, transaction_id: int) -> PPOBTransaction:
        """Proses pembayaran transaksi"""
        try:
            # Ambil transaksi
            transaction = self.db.query(PPOBTransaction).filter(
                PPOBTransaction.id == transaction_id
            ).first()
            
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
            if payment_result.get("status") == "success":
                transaction.status = TransactionStatus.SUCCESS
                transaction.provider_ref = payment_result.get("transaction_id")
                transaction.notes = payment_result.get("message")
            else:
                transaction.status = TransactionStatus.FAILED
                transaction.notes = payment_result.get("message", "Pembayaran gagal")
            
            self.db.commit()
            self.db.refresh(transaction)
            
            return transaction
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses pembayaran: {str(e)}"
            )
    
    def get_user_transactions(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[PPOBTransaction]:
        """Ambil riwayat transaksi user"""
        return self.db.query(PPOBTransaction).filter(
            PPOBTransaction.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[PPOBTransaction]:
        """Ambil transaksi berdasarkan ID"""
        return self.db.query(PPOBTransaction).filter(
            PPOBTransaction.id == transaction_id
        ).first()
