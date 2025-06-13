"""
PPOB Callback Handlers
Mengelola callback dari PPOB providers seperti Digiflazz
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging

from app.callbacks.base.base_handlers import WebhookCallbackHandler

logger = logging.getLogger(__name__)


class DigiflazzCallbackHandler(WebhookCallbackHandler):
    """Handler untuk Digiflazz PPOB callback/webhook"""
    
    def __init__(self, db: Session):
        super().__init__("DigiflazzCallback", "digiflazz")
        self.db = db
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Digiflazz webhook notification"""
        
        # Validasi required fields untuk Digiflazz
        required_fields = ['data']
        if not self.validate_data(data, required_fields):
            raise ValueError("Invalid Digiflazz webhook data")
        
        try:
            webhook_data = data.get('data', {})
            ref_id = webhook_data.get('ref_id')
            status = webhook_data.get('status', '').lower()
            trx_id = webhook_data.get('trx_id')
            message = webhook_data.get('message', '')
            sn = webhook_data.get('sn', '')
            
            if not ref_id:
                raise ValueError("Missing ref_id in Digiflazz webhook")
            
            # Update status transaksi PPOB
            await self._update_ppob_transaction(ref_id, status, webhook_data)
            
            # Kirim notifikasi
            await self._send_notification(ref_id, status, message)
            
            return {
                'success': True,
                'ref_id': ref_id,
                'status': status,
                'trx_id': trx_id,
                'message': 'Digiflazz callback processed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error processing Digiflazz callback: {str(e)}")
            raise
    
    async def _update_ppob_transaction(self, ref_id: str, status: str, webhook_data: Dict[str, Any]):
        """Update status transaksi PPOB berdasarkan callback"""
        try:
            # Import models (sesuaikan dengan model PPOB yang ada)
            from app.models.transaction import Transaction, TransactionStatus
            
            # Cari transaksi berdasarkan reference_id
            transaction = self.db.query(Transaction).filter(
                Transaction.reference_id == ref_id
            ).first()
            
            if not transaction:
                logger.warning(f"PPOB Transaction not found for ref_id: {ref_id}")
                return
            
            # Update status berdasarkan Digiflazz response
            if status == 'sukses':
                transaction.status = TransactionStatus.SUCCESS
                transaction.serial_number = webhook_data.get('sn', '')
            elif status == 'gagal':
                transaction.status = TransactionStatus.FAILED
            elif status == 'pending':
                transaction.status = TransactionStatus.PENDING
            
            # Update metadata
            transaction.provider_response = webhook_data
            transaction.provider_transaction_id = webhook_data.get('trx_id')
            
            self.db.commit()
            logger.info(f"PPOB Transaction {ref_id} status updated to {status}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating PPOB transaction status: {str(e)}")
            raise
    
    async def _send_notification(self, ref_id: str, status: str, message: str):
        """Kirim notifikasi setelah update status PPOB"""
        try:
            # Import notification service
            from app.domains.notification.services.notification_service import NotificationService
            from app.schemas.notification import NotificationCreate
            from app.models.notification import NotificationType
            
            # Cari user dari transaksi
            from app.models.transaction import Transaction
            transaction = self.db.query(Transaction).filter(
                Transaction.reference_id == ref_id
            ).first()
            
            if not transaction:
                return
            
            # Buat notifikasi
            notification_service = NotificationService(self.db)
            
            if status == 'sukses':
                notification_message = f"Transaksi PPOB {transaction.product_name} berhasil diproses"
            elif status == 'gagal':
                notification_message = f"Transaksi PPOB {transaction.product_name} gagal: {message}"
            else:
                notification_message = f"Transaksi PPOB {transaction.product_name} sedang diproses"
            
            notification_data = NotificationCreate(
                user_id=transaction.user_id,
                title="Update Status Transaksi PPOB",
                message=notification_message,
                notification_type=NotificationType.TRANSACTION
            )
            
            await notification_service.create_notification(notification_data)
            logger.info(f"PPOB notification sent for transaction {ref_id}")
            
        except Exception as e:
            logger.error(f"Error sending PPOB notification: {str(e)}")
            # Don't raise exception for notification errors


class PPOBCallbackFactory:
    """Factory untuk membuat PPOB callback handlers"""
    
    @staticmethod
    def create_handler(provider: str, db: Session) -> WebhookCallbackHandler:
        """Create callback handler berdasarkan provider"""
        
        if provider.lower() == 'digiflazz':
            return DigiflazzCallbackHandler(db)
        else:
            raise ValueError(f"Unsupported PPOB provider: {provider}")
