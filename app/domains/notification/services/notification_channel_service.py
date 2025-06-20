from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import aiohttp
import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.models.notification import NotificationChannel
from app.schemas.notification import NotificationSendRequest
from app.utils.exceptions import HTTPException

logger = logging.getLogger(__name__)

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
            
            # Tambahkan body email
            msg.attach(MIMEText(message, 'plain'))
            
            # Kirim email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, to_email, text)
            server.quit()
            
            logger.info(f"Email berhasil dikirim ke {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def send_discord(self, webhook_url: str, message: str, title: str = None) -> bool:
        """Kirim notifikasi via Discord webhook"""
        try:
            if not webhook_url:
                logger.warning("Discord webhook URL not configured")
                return False
            
            # Format pesan Discord
            embed = {
                "title": title or "Notifikasi",
                "description": message,
                "color": 0x00ff00,  # Warna hijau
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {
                "embeds": [embed]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info("Discord notification sent successfully")
                        return True
                    else:
                        logger.error(f"Discord webhook failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Discord notification: {str(e)}")
            return False
    
    async def send_telegram(self, bot_token: str, chat_id: str, message: str) -> bool:
        """Kirim notifikasi via Telegram"""
        try:
            if not bot_token or not chat_id:
                logger.warning("Telegram credentials not configured")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram notification sent successfully")
                        return True
                    else:
                        logger.error(f"Telegram API failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {str(e)}")
            return False
    
    async def send_notification(self, request: NotificationSendRequest) -> Dict[str, bool]:
        """Kirim notifikasi ke multiple channels"""
        results = {}
        
        for channel in request.channels:
            if channel == NotificationChannel.EMAIL:
                # Ambil email admin dari database atau konfigurasi
                admin_email = getattr(settings, 'ADMIN_EMAIL', '')
                if admin_email:
                    results[channel.value] = await self.send_email(
                        admin_email, request.title, request.message
                    )
                else:
                    results[channel.value] = False
                    
            elif channel == NotificationChannel.DISCORD:
                # Ambil Discord webhook URL dari konfigurasi
                webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', '')
                results[channel.value] = await self.send_discord(
                    webhook_url, request.message, request.title
                )
                
            elif channel == NotificationChannel.TELEGRAM:
                # Ambil Telegram credentials dari konfigurasi
                bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
                chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
                results[channel.value] = await self.send_telegram(
                    bot_token, chat_id, f"{request.title}\n\n{request.message}"
                )
        
        return results
