"""
Notification Callback Handlers
Mengelola callback dari berbagai notification providers dan webhooks
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
import logging
import json

from app.callbacks.base.base_handlers import WebhookCallbackHandler

logger = logging.getLogger(__name__)


class NotificationWebhookHandler(WebhookCallbackHandler):
    """Handler untuk notification webhooks dari berbagai provider"""
    
    def __init__(self, db: Session):
        super().__init__("NotificationWebhook", "notification")
        self.db = db
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle notification webhook"""
        webhook_type = data.get('webhook_type')
        webhook_data = data.get('data', {})
        
        if not webhook_type:
            raise ValueError("Missing webhook_type")
        
        try:
            # Route ke handler yang sesuai
            if webhook_type == 'digiflazz':
                return await self._handle_digiflazz_webhook(webhook_data)
            elif webhook_type == 'midtrans':
                return await self._handle_midtrans_webhook(webhook_data)
            elif webhook_type == 'whatsapp':
                return await self._handle_whatsapp_webhook(webhook_data)
            elif webhook_type == 'email':
                return await self._handle_email_webhook(webhook_data)
            else:
                logger.warning(f"Unknown webhook type: {webhook_type}")
                return {'success': False, 'message': f'Unknown webhook type: {webhook_type}'}
                
        except Exception as e:
            logger.error(f"Error processing notification webhook: {str(e)}")
            raise
    
    async def _handle_digiflazz_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Digiflazz webhook notification"""
        try:
            # Import dan gunakan existing webhook service
            from app.domains.notification.services.notification_service import WebhookService
            from app.schemas.notification import WebhookLogCreate
            
            webhook_service = WebhookService(self.db)
            
            # Log webhook request
            log_data = WebhookLogCreate(
                webhook_type="digiflazz",
                request_method="POST",
                request_url="/webhook/digiflazz",
                request_body=json.dumps(webhook_data),
                processed=False
            )
            
            webhook_log = await webhook_service.log_webhook(log_data)
            
            # Process webhook
            result = await webhook_service.process_digiflazz_webhook(webhook_data)
            
            # Update log status
            webhook_log.processed = result
            webhook_log.response_status = 200 if result else 500
            self.db.commit()
            
            return {
                'success': result,
                'message': 'Digiflazz webhook processed',
                'webhook_log_id': webhook_log.id
            }
            
        except Exception as e:
            logger.error(f"Error handling Digiflazz webhook: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_midtrans_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Midtrans webhook notification"""
        try:
            # Import Midtrans callback handler
            from app.callbacks.payment.midtrans_callback import MidtransCallbackHandler
            
            midtrans_handler = MidtransCallbackHandler(self.db)
            result = await midtrans_handler.process_webhook(webhook_data)
            
            return {
                'success': result.get('success', False),
                'message': 'Midtrans webhook processed',
                'order_id': result.get('order_id'),
                'status': result.get('status')
            }
            
        except Exception as e:
            logger.error(f"Error handling Midtrans webhook: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_whatsapp_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp webhook notification"""
        try:
            # Process WhatsApp delivery status, incoming messages, etc.
            message_id = webhook_data.get('message_id')
            status = webhook_data.get('status')
            phone_number = webhook_data.get('phone_number')
            
            logger.info(f"WhatsApp webhook - Message: {message_id}, Status: {status}, Phone: {phone_number}")
            
            # Update message status di database jika diperlukan
            await self._update_whatsapp_message_status(message_id, status)
            
            return {
                'success': True,
                'message': 'WhatsApp webhook processed',
                'message_id': message_id,
                'status': status
            }
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp webhook: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_email_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Email webhook notification"""
        try:
            # Process email delivery status, bounces, complaints, etc.
            message_id = webhook_data.get('message_id')
            event_type = webhook_data.get('event_type')  # delivered, bounced, complained
            email = webhook_data.get('email')
            
            logger.info(f"Email webhook - Message: {message_id}, Event: {event_type}, Email: {email}")
            
            # Update email status di database
            await self._update_email_status(message_id, event_type)
            
            return {
                'success': True,
                'message': 'Email webhook processed',
                'message_id': message_id,
                'event_type': event_type
            }
            
        except Exception as e:
            logger.error(f"Error handling Email webhook: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _update_whatsapp_message_status(self, message_id: str, status: str):
        """Update WhatsApp message status"""
        try:
            # Implementasi update status pesan WhatsApp
            # Sesuaikan dengan model yang ada
            logger.debug(f"Updating WhatsApp message {message_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating WhatsApp message status: {str(e)}")
    
    async def _update_email_status(self, message_id: str, event_type: str):
        """Update email status"""
        try:
            # Implementasi update status email
            # Sesuaikan dengan model yang ada
            logger.debug(f"Updating email {message_id} status to {event_type}")
            
        except Exception as e:
            logger.error(f"Error updating email status: {str(e)}")


class DiscordWebhookHandler(WebhookCallbackHandler):
    """Handler untuk Discord webhooks"""
    
    def __init__(self):
        super().__init__("DiscordWebhook", "discord_webhook")
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Discord webhook"""
        webhook_url = data.get('webhook_url')
        title = data.get('title', 'Notification')
        message = data.get('message', '')
        color = data.get('color', 0x00ff00)  # Green default
        
        if not webhook_url or not message:
            raise ValueError("Missing webhook_url or message")
        
        try:
            # Send Discord webhook
            result = await self._send_discord_webhook(webhook_url, title, message, color)
            
            return {
                'success': result,
                'message': 'Discord webhook sent' if result else 'Discord webhook failed',
                'webhook_url': webhook_url
            }
            
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {str(e)}")
            raise
    
    async def _send_discord_webhook(self, webhook_url: str, title: str, message: str, color: int) -> bool:
        """Send Discord webhook"""
        try:
            import aiohttp
            
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": "2023-01-01T00:00:00.000Z"  # Current timestamp
            }
            
            payload = {
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("Discord webhook sent successfully")
                        return True
                    else:
                        logger.error(f"Discord webhook failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Discord webhook: {str(e)}")
            return False


class TelegramWebhookHandler(WebhookCallbackHandler):
    """Handler untuk Telegram webhooks"""
    
    def __init__(self, bot_token: str):
        super().__init__("TelegramWebhook", "telegram_webhook")
        self.bot_token = bot_token
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Telegram webhook"""
        chat_id = data.get('chat_id')
        message = data.get('message', '')
        parse_mode = data.get('parse_mode', 'HTML')
        
        if not chat_id or not message:
            raise ValueError("Missing chat_id or message")
        
        try:
            # Send Telegram message
            result = await self._send_telegram_message(chat_id, message, parse_mode)
            
            return {
                'success': result,
                'message': 'Telegram message sent' if result else 'Telegram message failed',
                'chat_id': chat_id
            }
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            raise
    
    async def _send_telegram_message(self, chat_id: str, message: str, parse_mode: str) -> bool:
        """Send Telegram message"""
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram message sent successfully")
                        return True
                    else:
                        logger.error(f"Telegram message failed: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Telegram message: {str(e)}")
            return False


class NotificationCallbackFactory:
    """Factory untuk membuat notification callback handlers"""
    
    @staticmethod
    def create_webhook_handler(webhook_type: str, db: Session = None, **kwargs) -> WebhookCallbackHandler:
        """Create webhook handler berdasarkan type"""
        
        if webhook_type == 'notification':
            if not db:
                raise ValueError("Database session required for notification webhook")
            return NotificationWebhookHandler(db)
        elif webhook_type == 'discord':
            return DiscordWebhookHandler()
        elif webhook_type == 'telegram':
            bot_token = kwargs.get('bot_token')
            if not bot_token:
                raise ValueError("Bot token required for Telegram webhook")
            return TelegramWebhookHandler(bot_token)
        else:
            raise ValueError(f"Unsupported webhook type: {webhook_type}")
