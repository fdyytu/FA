from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
from app.models.notification import (
    Notification, AdminNotificationSetting, WebhookLog,
    NotificationType, NotificationChannel, NotificationStatus
)
from app.models.admin import Admin
from app.schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    AdminNotificationSettingCreate, AdminNotificationSettingUpdate,
    NotificationSendRequest, WebhookLogCreate
)
from app.utils.exceptions import HTTPException
import logging
import aiohttp
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service untuk mengelola notifikasi - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        """Membuat notifikasi baru"""
        try:
            db_notification = Notification(**notification_data.dict())
            
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)
            
            logger.info(f"Notifikasi berhasil dibuat: {db_notification.id}")
            return NotificationResponse.from_orm(db_notification)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat notifikasi: {str(e)}")
    
    async def get_user_notifications(self, user_id: int, page: int = 1, limit: int = 10) -> List[NotificationResponse]:
        """Mendapatkan notifikasi user"""
        try:
            offset = (page - 1) * limit
            notifications = self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
            
            return [NotificationResponse.from_orm(n) for n in notifications]
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal mengambil notifikasi: {str(e)}")
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> NotificationResponse:
        """Tandai notifikasi sebagai sudah dibaca"""
        try:
            notification = self.db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if not notification:
                raise HTTPException(status_code=404, detail="Notifikasi tidak ditemukan")
            
            notification.is_read = True
            notification.read_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(notification)
            
            return NotificationResponse.from_orm(notification)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking notification as read: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal menandai notifikasi: {str(e)}")

class NotificationChannelService:
    """Service untuk mengirim notifikasi ke berbagai channel - mengikuti prinsip Open/Closed"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def send_email(self, to_email: str, subject: str, message: str) -> bool:
        """Kirim notifikasi via email"""
        try:
            # Konfigurasi SMTP (sesuaikan dengan provider email Anda)
            smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_username = getattr(settings, 'SMTP_USERNAME', '')
            smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
            
            if not smtp_username or not smtp_password:
                logger.warning("SMTP credentials not configured")
                return False
            
            # Buat pesan email
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Kirim email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, to_email, text)
            server.quit()
            
            logger.info(f"Email berhasil dikirim ke: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Kirim notifikasi via WhatsApp (menggunakan API WhatsApp Business)"""
        try:
            # Konfigurasi WhatsApp API (sesuaikan dengan provider Anda)
            wa_api_url = getattr(settings, 'WHATSAPP_API_URL', '')
            wa_api_token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
            
            if not wa_api_url or not wa_api_token:
                logger.warning("WhatsApp API not configured")
                return False
            
            # Format nomor telepon (hapus karakter non-digit)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if not clean_phone.startswith('62'):
                clean_phone = '62' + clean_phone.lstrip('0')
            
            # Payload untuk API WhatsApp
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            headers = {
                "Authorization": f"Bearer {wa_api_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(wa_api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"WhatsApp berhasil dikirim ke: {phone_number}")
                        return True
                    else:
                        logger.error(f"WhatsApp API error: {response.status}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp: {str(e)}")
            return False
    
    async def send_discord(self, webhook_url: str, title: str, message: str) -> bool:
        """Kirim notifikasi via Discord webhook"""
        try:
            payload = {
                "embeds": [
                    {
                        "title": title,
                        "description": message,
                        "color": 5814783,  # Blue color
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("Discord notification sent successfully")
                        return True
                    else:
                        logger.error(f"Discord webhook error: {response.status}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
    
    async def send_push_notification(self, user_token: str, title: str, message: str) -> bool:
        """Kirim push notification (implementasi dasar)"""
        try:
            # Implementasi push notification menggunakan FCM atau provider lain
            # Ini adalah contoh dasar, sesuaikan dengan provider yang digunakan
            
            fcm_server_key = getattr(settings, 'FCM_SERVER_KEY', '')
            if not fcm_server_key:
                logger.warning("FCM server key not configured")
                return False
            
            payload = {
                "to": user_token,
                "notification": {
                    "title": title,
                    "body": message
                }
            }
            
            headers = {
                "Authorization": f"key={fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://fcm.googleapis.com/fcm/send",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info("Push notification sent successfully")
                        return True
                    else:
                        logger.error(f"FCM error: {response.status}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False

class AdminNotificationService:
    """Service untuk mengelola notifikasi admin - mengikuti prinsip Single Responsibility"""
    
    def __init__(self, db: Session):
        self.db = db
        self.channel_service = NotificationChannelService(db)
    
    async def send_admin_notification(self, notification_request: NotificationSendRequest):
        """Kirim notifikasi ke admin berdasarkan pengaturan mereka"""
        try:
            # Ambil semua admin yang aktif
            admins = self.db.query(Admin).filter(Admin.is_active == True).all()
            
            for admin in admins:
                # Ambil pengaturan notifikasi admin
                settings = self.db.query(AdminNotificationSetting).filter(
                    and_(
                        AdminNotificationSetting.admin_id == admin.id,
                        AdminNotificationSetting.notification_type == notification_request.notification_type,
                        AdminNotificationSetting.is_enabled == True
                    )
                ).all()
                
                # Kirim ke setiap channel yang diaktifkan
                for setting in settings:
                    if setting.channel in notification_request.channels:
                        await self._send_to_channel(
                            setting,
                            notification_request.title,
                            notification_request.message
                        )
            
            logger.info(f"Admin notification sent: {notification_request.title}")
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal kirim notifikasi admin: {str(e)}")
    
    async def _send_to_channel(self, setting: AdminNotificationSetting, title: str, message: str):
        """Kirim notifikasi ke channel tertentu"""
        try:
            success = False
            
            if setting.channel == NotificationChannel.EMAIL and setting.email:
                success = await self.channel_service.send_email(setting.email, title, message)
            
            elif setting.channel == NotificationChannel.WHATSAPP and setting.phone_number:
                success = await self.channel_service.send_whatsapp(setting.phone_number, f"{title}\n\n{message}")
            
            elif setting.channel == NotificationChannel.DISCORD and setting.webhook_url:
                success = await self.channel_service.send_discord(setting.webhook_url, title, message)
            
            # Log hasil pengiriman
            if success:
                logger.info(f"Notification sent via {setting.channel.value} to admin {setting.admin_id}")
            else:
                logger.error(f"Failed to send notification via {setting.channel.value} to admin {setting.admin_id}")
                
        except Exception as e:
            logger.error(f"Error sending to channel {setting.channel.value}: {str(e)}")
    
    async def create_admin_notification_setting(self, setting_data: AdminNotificationSettingCreate) -> AdminNotificationSetting:
        """Buat pengaturan notifikasi admin baru"""
        try:
            db_setting = AdminNotificationSetting(**setting_data.dict())
            
            self.db.add(db_setting)
            self.db.commit()
            self.db.refresh(db_setting)
            
            logger.info(f"Admin notification setting created for admin {setting_data.admin_id}")
            return db_setting
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating admin notification setting: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Gagal membuat pengaturan notifikasi: {str(e)}")

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
