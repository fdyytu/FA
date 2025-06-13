"""
Payment Callback Handlers
Mengelola callback dari payment gateway seperti Midtrans
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

from app.callbacks.base.base_handlers import WebhookCallbackHandler
from app.domains.payment.services.midtrans_service import midtrans_service

logger = logging.getLogger(__name__)


class MidtransCallbackHandler(WebhookCallbackHandler):
    """Handler untuk Midtrans payment callback/webhook"""
    
    def __init__(self, db: Session):
        super().__init__("MidtransCallback", "midtrans")
        self.db = db
        self.midtrans_service = midtrans_service
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Midtrans webhook notification"""
        
        # Validasi required fields untuk Midtrans
        required_fields = ['order_id', 'transaction_status']
        if not self.validate_data(data, required_fields):
            raise ValueError("Invalid Midtrans webhook data")
        
        try:
            # Verify notification dengan Midtrans service
            verification_result = self.midtrans_service.verify_notification(data)
            
            if not verification_result['success']:
                raise Exception(f"Midtrans verification failed: {verification_result['error']}")
            
            order_id = verification_result['order_id']
            status = verification_result['status']
            transaction_status = verification_result['transaction_status']
            
            # Update status transaksi di database
            await self._update_transaction_status(order_id, status, verification_result)
            
            # Kirim notifikasi jika diperlukan
            await self._send_notification(order_id, status)
            
            return {
                'success': True,
                'order_id': order_id,
                'status': status,
                'transaction_status': transaction_status,
                'message': 'Midtrans callback processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing Midtrans callback: {str(e)}")
            raise
    
    async def _update_transaction_status(self, order_id: str, status: str, verification_data: Dict[str, Any]):
        """Update status transaksi berdasarkan callback"""
        try:
            # Import models
            from app.models.wallet import TopUpRequest, TopUpStatus
            
            # Cari transaksi berdasarkan midtrans_order_id
            transaction = self.db.query(TopUpRequest).filter(
                TopUpRequest.midtrans_order_id == order_id
            ).first()
            
            if not transaction:
                logger.warning(f"Transaction not found for order_id: {order_id}")
                return
            
            # Update status berdasarkan Midtrans status
            if status == 'success':
                transaction.status = TopUpStatus.APPROVED
                
                # Update saldo user jika berhasil
                from app.models.wallet import Wallet
                wallet = self.db.query(Wallet).filter(
                    Wallet.user_id == transaction.user_id
                ).first()
                
                if wallet:
                    wallet.balance += transaction.amount
                    
                    # Buat record transaksi wallet
                    from app.models.wallet import WalletTransaction, TransactionType
                    wallet_transaction = WalletTransaction(
                        wallet_id=wallet.id,
                        transaction_type=TransactionType.TOPUP,
                        amount=transaction.amount,
                        description=f"Top up via Midtrans - {order_id}",
                        reference_id=order_id
                    )
                    self.db.add(wallet_transaction)
                    
            elif status == 'failed':
                transaction.status = TopUpStatus.REJECTED
            elif status == 'pending':
                transaction.status = TopUpStatus.PENDING
            
            # Update metadata
            transaction.midtrans_response = verification_data.get('raw_data', {})
            
            self.db.commit()
            logger.info(f"Transaction {order_id} status updated to {status}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating transaction status: {str(e)}")
            raise
    
    async def _send_notification(self, order_id: str, status: str):
        """Kirim notifikasi setelah update status"""
        try:
            # Import notification service
            from app.domains.notification.services.notification_service import NotificationService
            from app.schemas.notification import NotificationCreate
            from app.models.notification import NotificationType
            
            # Cari user dari transaksi
            from app.models.wallet import TopUpRequest
            transaction = self.db.query(TopUpRequest).filter(
                TopUpRequest.midtrans_order_id == order_id
            ).first()
            
            if not transaction:
                return
            
            # Buat notifikasi
            notification_service = NotificationService(self.db)
            
            if status == 'success':
                message = f"Top up sebesar Rp {transaction.amount:,.0f} berhasil diproses"
            elif status == 'failed':
                message = f"Top up sebesar Rp {transaction.amount:,.0f} gagal diproses"
            else:
                message = f"Top up sebesar Rp {transaction.amount:,.0f} sedang diproses"
            
            notification_data = NotificationCreate(
                user_id=transaction.user_id,
                title="Update Status Top Up",
                message=message,
                notification_type=NotificationType.PAYMENT
            )
            
            await notification_service.create_notification(notification_data)
            logger.info(f"Notification sent for transaction {order_id}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            # Don't raise exception for notification errors
