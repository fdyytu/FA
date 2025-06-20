"""
PPOB Payment Service
Service untuk menangani operasi pembayaran PPOB
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from decimal import Decimal

from app.common.base_classes.base_service import BaseService
from app.domains.ppob.repositories.ppob_repository import PPOBRepository
from app.domains.ppob.models.ppob import PPOBTransaction, TransactionStatus
from app.domains.ppob.schemas.ppob_schemas import PPOBInquiryRequest, PPOBInquiryResponse, PPOBPaymentRequest

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

from app.infrastructure.config.settings import settings


class PPOBPaymentService(BaseService):
    """Service untuk menangani operasi pembayaran PPOB"""
    
    def __init__(self, repository: PPOBRepository):
        super().__init__(repository)
        self.admin_service = AdminConfigService(repository.db) if AdminConfigService else None
        self.margin_service = PPOBMarginService(repository.db) if PPOBMarginService else None
        self.provider = self._get_provider()
    
    def _get_provider(self):
        """Ambil provider berdasarkan konfigurasi admin (Factory Pattern)"""
        try:
            if self.admin_service:
                provider_config = self.admin_service.get_ppob_provider_config()
                provider_name = provider_config.get('provider', 'default')
                
                if provider_name == 'digiflazz' and DigiflazzProvider:
                    return DigiflazzProvider(
                        username=provider_config.get('username'),
                        api_key=provider_config.get('api_key'),
                        production=provider_config.get('production', False)
                    )
            
            # Fallback to default provider
            if DefaultPPOBProvider:
                return DefaultPPOBProvider()
            
            return None
        except Exception as e:
            # Log error and return None
            return None
    
    async def inquiry(self, request: PPOBInquiryRequest) -> PPOBInquiryResponse:
        """Lakukan inquiry ke provider"""
        try:
            if not self.provider:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PPOB provider not available"
                )
            
            # Get product info
            product = await self.repository.get_product_by_code(request.product_code)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            
            # Call provider inquiry
            inquiry_result = await self.provider.inquiry(
                product_code=request.product_code,
                customer_number=request.customer_number
            )
            
            if not inquiry_result.get('success', False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=inquiry_result.get('message', 'Inquiry failed')
                )
            
            # Calculate final price with margin
            base_price = Decimal(str(inquiry_result.get('amount', product.price)))
            margin = self._calculate_margin(product, base_price)
            final_price = base_price + margin
            
            return PPOBInquiryResponse(
                success=True,
                product_code=request.product_code,
                customer_number=request.customer_number,
                customer_name=inquiry_result.get('customer_name', ''),
                amount=final_price,
                admin_fee=inquiry_result.get('admin_fee', 0),
                total_amount=final_price + Decimal(str(inquiry_result.get('admin_fee', 0))),
                message=inquiry_result.get('message', 'Inquiry successful'),
                ref_id=inquiry_result.get('ref_id', '')
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Inquiry error: {str(e)}"
            )
    
    async def process_payment(self, transaction_id: int) -> PPOBTransaction:
        """Proses pembayaran ke provider"""
        try:
            if not self.provider:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PPOB provider not available"
                )
            
            # Get transaction
            transaction = await self.repository.get_transaction_by_id(transaction_id)
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found"
                )
            
            if transaction.status != TransactionStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Transaction is not in pending status"
                )
            
            # Update status to processing
            await self.repository.update_transaction(transaction_id, {
                'status': TransactionStatus.PROCESSING
            })
            
            try:
                # Call provider payment
                payment_result = await self.provider.payment(
                    product_code=transaction.product_code,
                    customer_number=transaction.customer_number,
                    amount=transaction.amount,
                    ref_id=transaction.reference_id
                )
                
                if payment_result.get('success', False):
                    # Payment successful
                    updated_transaction = await self.repository.update_transaction(transaction_id, {
                        'status': TransactionStatus.SUCCESS,
                        'provider_ref_id': payment_result.get('provider_ref_id'),
                        'serial_number': payment_result.get('serial_number'),
                        'notes': payment_result.get('message', 'Payment successful')
                    })
                else:
                    # Payment failed
                    updated_transaction = await self.repository.update_transaction(transaction_id, {
                        'status': TransactionStatus.FAILED,
                        'notes': payment_result.get('message', 'Payment failed')
                    })
                
                return updated_transaction
                
            except Exception as provider_error:
                # Provider error, mark as failed
                await self.repository.update_transaction(transaction_id, {
                    'status': TransactionStatus.FAILED,
                    'notes': f'Provider error: {str(provider_error)}'
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Payment processing failed: {str(provider_error)}"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment error: {str(e)}"
            )
    
    def _calculate_margin(self, product, base_price: Decimal) -> Decimal:
        """Hitung margin berdasarkan konfigurasi"""
        try:
            if self.margin_service:
                margin_config = self.margin_service.get_margin_config(product.category_id)
                
                if margin_config.get('type') == 'percentage':
                    margin_percent = Decimal(str(margin_config.get('value', 0))) / 100
                    return base_price * margin_percent
                elif margin_config.get('type') == 'fixed':
                    return Decimal(str(margin_config.get('value', 0)))
            
            # Default margin 5%
            return base_price * Decimal('0.05')
            
        except Exception:
            # Fallback to 5% margin
            return base_price * Decimal('0.05')
    
    async def check_transaction_status(self, transaction_id: int) -> Dict[str, Any]:
        """Cek status transaksi dari provider"""
        try:
            if not self.provider:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="PPOB provider not available"
                )
            
            transaction = await self.repository.get_transaction_by_id(transaction_id)
            if not transaction:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transaction not found"
                )
            
            # Check status from provider
            status_result = await self.provider.check_status(
                ref_id=transaction.reference_id
            )
            
            return {
                'transaction_id': transaction_id,
                'local_status': transaction.status.value,
                'provider_status': status_result.get('status'),
                'provider_message': status_result.get('message'),
                'last_updated': transaction.updated_at.isoformat() if transaction.updated_at else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Status check error: {str(e)}"
            )
