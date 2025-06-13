"""
Callback Manager
Mengelola dan mengkoordinasikan semua callback handlers
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging

from app.callbacks.base.base_handlers import BaseCallbackHandler, callback_registry
from app.callbacks.payment.midtrans_callback import MidtransCallbackHandler
from app.callbacks.ppob.ppob_callbacks import PPOBCallbackFactory
from app.callbacks.discord.discord_callbacks import DiscordBotEventHandler, DiscordSlashCommandHandler
from app.callbacks.file_monitor.file_callbacks import FileMonitorCallbackHandler, FileUploadCallbackHandler
from app.callbacks.notification.notification_callbacks import NotificationCallbackFactory

logger = logging.getLogger(__name__)


class CallbackManager:
    """Manager untuk mengelola semua callback handlers"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self._handlers: Dict[str, BaseCallbackHandler] = {}
        self._initialize_handlers()
    
    def _initialize_handlers(self):
        """Initialize semua callback handlers"""
        try:
            # Payment callbacks
            if self.db:
                self.register_handler('midtrans_payment', MidtransCallbackHandler(self.db))
            
            # File monitor callbacks
            self.register_handler('file_monitor', FileMonitorCallbackHandler())
            self.register_handler('file_upload', FileUploadCallbackHandler())
            
            logger.info("Callback handlers initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing callback handlers: {str(e)}")
    
    def register_handler(self, callback_type: str, handler: BaseCallbackHandler):
        """Register callback handler"""
        self._handlers[callback_type] = handler
        callback_registry.register(callback_type, handler)
        logger.info(f"Registered callback handler: {callback_type}")
    
    def get_handler(self, callback_type: str) -> Optional[BaseCallbackHandler]:
        """Get callback handler by type"""
        return self._handlers.get(callback_type)
    
    async def process_callback(self, callback_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process callback dengan handler yang sesuai"""
        try:
            handler = self.get_handler(callback_type)
            if not handler:
                raise ValueError(f"No handler found for callback type: {callback_type}")
            
            logger.info(f"Processing callback: {callback_type}")
            result = await handler.handle(data)
            
            logger.info(f"Callback {callback_type} processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing callback {callback_type}: {str(e)}")
            raise
    
    async def process_webhook(self, webhook_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook dengan handler yang sesuai"""
        try:
            # Route webhook ke handler yang tepat
            if webhook_type == 'midtrans':
                return await self.process_callback('midtrans_payment', request_data)
            elif webhook_type == 'digiflazz':
                # Create PPOB handler untuk Digiflazz
                if self.db:
                    handler = PPOBCallbackFactory.create_handler('digiflazz', self.db)
                    return await handler.process_webhook(request_data)
                else:
                    raise ValueError("Database session required for PPOB webhook")
            elif webhook_type in ['discord', 'telegram', 'notification']:
                # Create notification webhook handler
                if self.db:
                    handler = NotificationCallbackFactory.create_webhook_handler(webhook_type, self.db)
                    return await handler.process_webhook(request_data)
                else:
                    raise ValueError("Database session required for notification webhook")
            else:
                raise ValueError(f"Unknown webhook type: {webhook_type}")
                
        except Exception as e:
            logger.error(f"Error processing webhook {webhook_type}: {str(e)}")
            raise
    
    async def process_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process event dengan handler yang sesuai"""
        try:
            # Route event ke handler yang tepat
            if event_type.startswith('file_'):
                return await self.process_callback('file_monitor', {
                    'type': event_type.replace('file_', ''),
                    **event_data
                })
            elif event_type.startswith('discord_'):
                # Discord events perlu bot instance
                logger.info(f"Discord event {event_type} received")
                return {'success': True, 'message': f'Discord event {event_type} logged'}
            elif event_type == 'file_upload':
                return await self.process_callback('file_upload', event_data)
            else:
                raise ValueError(f"Unknown event type: {event_type}")
                
        except Exception as e:
            logger.error(f"Error processing event {event_type}: {str(e)}")
            raise
    
    def setup_discord_handlers(self, bot):
        """Setup Discord bot event handlers"""
        try:
            # Register Discord event handlers
            discord_event_handler = DiscordBotEventHandler(bot)
            discord_slash_handler = DiscordSlashCommandHandler(bot)
            
            self.register_handler('discord_events', discord_event_handler)
            self.register_handler('discord_slash', discord_slash_handler)
            
            logger.info("Discord handlers setup successfully")
            
        except Exception as e:
            logger.error(f"Error setting up Discord handlers: {str(e)}")
    
    def list_handlers(self) -> Dict[str, str]:
        """List semua registered handlers"""
        return {k: v.name for k, v in self._handlers.items()}
    
    def get_handler_stats(self) -> Dict[str, Any]:
        """Get statistics dari semua handlers"""
        stats = {
            'total_handlers': len(self._handlers),
            'handlers': {}
        }
        
        for callback_type, handler in self._handlers.items():
            stats['handlers'][callback_type] = {
                'name': handler.name,
                'created_at': handler.created_at.isoformat() if hasattr(handler, 'created_at') else None,
                'type': type(handler).__name__
            }
        
        return stats


class CallbackRouter:
    """Router untuk mengarahkan callback ke handler yang tepat"""
    
    def __init__(self, callback_manager: CallbackManager):
        self.callback_manager = callback_manager
    
    async def route_webhook(self, webhook_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route webhook ke handler yang tepat"""
        return await self.callback_manager.process_webhook(webhook_type, request_data)
    
    async def route_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route event ke handler yang tepat"""
        return await self.callback_manager.process_event(event_type, event_data)
    
    async def route_callback(self, callback_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Route callback ke handler yang tepat"""
        return await self.callback_manager.process_callback(callback_type, data)


# Global callback manager instance
_callback_manager: Optional[CallbackManager] = None


def get_callback_manager(db: Session = None) -> CallbackManager:
    """Get global callback manager instance"""
    global _callback_manager
    
    if _callback_manager is None:
        _callback_manager = CallbackManager(db)
    
    return _callback_manager


def initialize_callbacks(db: Session = None):
    """Initialize callback system"""
    global _callback_manager
    _callback_manager = CallbackManager(db)
    logger.info("Callback system initialized")
    return _callback_manager
