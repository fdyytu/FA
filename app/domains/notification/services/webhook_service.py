from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json

from app.models.notification import WebhookLog, NotificationType, NotificationChannel
from app.schemas.notification import WebhookLogCreate, NotificationSendRequest
from app.utils.exceptions import HTTPException
from .admin_notification_service import AdminNotificationService

logger = logging.getLogger(__name__)

class WebhookService:
    """Service untuk mengelola webhook - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def log_webhook(self, webhook_data: WebhookLogCreate) -> WebhookLog:
        """Log webhook request"""
        try:
            db_log = WebhookLog(**webhook_data.dict())
            
            self.db.add(db_log)
            self.db.commit()
            self.db.refresh(db_log)
            
            return db_log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging webhook: {str(e)}")
            raise e
    
    async def process_digiflazz_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Proses webhook dari Digiflazz"""
        try:
            # Log webhook request
            log_data = WebhookLogCreate(
                webhook_type="digiflazz",
                request_method="POST",
                request_url="/webhook/digiflazz",
                request_body=json.dumps(webhook_data),
                processed=False
            )
            
            webhook_log = await self.log_webhook(log_data)
            
            # Proses data webhook Digiflazz
            # Implementasi sesuai dengan format webhook Digiflazz
            ref_id = webhook_data.get('data', {}).get('ref_id')
            status = webhook_data.get('data', {}).get('status', '').lower()
            
            if ref_id:
                # Update status transaksi berdasarkan ref_id
                from app.services.transaction_service import TransactionService
                from app.schemas.transaction import TransactionUpdate, TransactionStatusEnum
                
                transaction_service = TransactionService(self.db)
                
                # Cari transaksi berdasarkan reference_id
                from app.models.transaction import Transaction
                transaction = self.db.query(Transaction).filter(
                    Transaction.reference_id == ref_id
                ).first()
                
                if transaction:
                    # Update status transaksi
                    if status == 'sukses':
                        update_data = TransactionUpdate(status=TransactionStatusEnum.SUCCESS)
                    elif status == 'gagal':
                        update_data = TransactionUpdate(status=TransactionStatusEnum.FAILED)
                    else:
                        update_data = TransactionUpdate(status=TransactionStatusEnum.PENDING)
                    
                    await transaction_service.update_transaction(transaction.id, update_data)
                    
                    # Kirim notifikasi ke admin
                    admin_service = AdminNotificationService(self.db)
                    notification_request = NotificationSendRequest(
                        title="Update Status Transaksi",
                        message=f"Transaksi {transaction.transaction_code} status: {status}",
                        notification_type=NotificationType.TRANSACTION,
                        channels=[NotificationChannel.DISCORD, NotificationChannel.EMAIL]
                    )
                    
                    await admin_service.send_admin_notification(notification_request)
            
            # Update log sebagai processed
            webhook_log.processed = True
            webhook_log.response_status = 200
            self.db.commit()
            
            logger.info(f"Digiflazz webhook processed successfully: {ref_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Digiflazz webhook: {str(e)}")
            
            # Update log dengan error
            if 'webhook_log' in locals():
                webhook_log.error_message = str(e)
                webhook_log.response_status = 500
                self.db.commit()
            
            return False
    
    async def get_webhook_logs(self, webhook_type: str = None, page: int = 1, limit: int = 10) -> List[WebhookLog]:
        """Ambil log webhook dengan pagination"""
        try:
            offset = (page - 1) * limit
            query = self.db.query(WebhookLog)
            
            if webhook_type:
                query = query.filter(WebhookLog.webhook_type == webhook_type)
            
            logs = query.order_by(WebhookLog.created_at.desc()).offset(offset).limit(limit).all()
            
            return logs
            
        except Exception as e:
            logger.error(f"Error getting webhook logs: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil log webhook: {str(e)}")
    
    async def retry_failed_webhook(self, webhook_log_id: int) -> bool:
        """Retry webhook yang gagal"""
        try:
            webhook_log = self.db.query(WebhookLog).filter(WebhookLog.id == webhook_log_id).first()
            
            if not webhook_log:
                raise HTTPException(status_code=404, detail="Log webhook tidak ditemukan")
            
            if webhook_log.processed:
                raise HTTPException(status_code=400, detail="Webhook sudah berhasil diproses")
            
            # Parse request body dan proses ulang
            webhook_data = json.loads(webhook_log.request_body)
            
            if webhook_log.webhook_type == "digiflazz":
                result = await self.process_digiflazz_webhook(webhook_data)
                return result
            
            # Tambahkan handler untuk webhook type lain di sini
            
            return False
            
        except Exception as e:
            logger.error(f"Error retrying webhook: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal retry webhook: {str(e)}")
